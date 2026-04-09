import streamlit as st
import json

from backend.models.schemas import RecommendationRequest
from backend.services.orchestrator import rank_with_llm_or_fallback
from backend.services.retrieval import get_ranked_candidates, fetch_locations
from backend.services.validators import normalize_request, validate_semantics

st.set_page_config(page_title="Zomato AI Backend Tester", layout="wide")

st.title("Zomato AI Backend - Streamlit Deployment")
st.markdown("Use this interface to test the backend logic directly via Streamlit.")

BANGALORE_LOCALITIES = ["Whitefield", "Koramangala", "Indiranagar", "Jayanagar", "Yelahanka", "HSR Layout", "Malleshwaram", "JP Nagar", "Marathahalli", "Bellandur"]

with st.sidebar:
    st.header("Search Filters")
    try:
        available_locations = fetch_locations()
        if not available_locations:
            available_locations = BANGALORE_LOCALITIES
    except Exception:
        available_locations = BANGALORE_LOCALITIES

    location = st.selectbox("Location", available_locations)
    budget = st.number_input("Budget (Cost for Two)", min_value=100.0, value=1000.0, step=100.0)
    cuisines_str = st.text_input("Cuisines (comma-separated)", value="Italian, Chinese")
    min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
    preferences = st.text_area("Additional Preferences", value="")

if st.button("Get Recommendations"):
    cuisines = [c.strip() for c in cuisines_str.split(",") if c.strip()]
    
    payload_dict = {
        "location": location,
        "budget": budget,
        "cuisines": cuisines,
        "min_rating": min_rating,
        "additional_preferences": preferences.strip() or None
    }
    
    try:
        req = RecommendationRequest(**payload_dict)
        validate_semantics(req)
        normalized = normalize_request(req)
    except Exception as e:
        st.error(f"Validation Error: {e}")
        st.stop()
    
    from backend.services.retrieval import Candidate

    with st.spinner("Fetching candidates from database..."):
        try:
            candidates = get_ranked_candidates(normalized)
        except Exception:
            candidates = []
            
    if not candidates:
        st.info("Using simulated data (Database not connected in Cloud deploy).")
        candidates = [
            Candidate(
                id="mock-1",
                name="Truffles",
                city="Bangalore",
                locality="Koramangala",
                cuisines=["Italian", "Continental"],
                avg_cost_for_two=900,
                rating=4.5,
                matched_features=["cuisine_match", "rating_threshold_match", "budget_fit"],
                heuristic_score=0.9
            ),
            Candidate(
                id="mock-2",
                name="Meghana Foods",
                city="Bangalore",
                locality="Indiranagar",
                cuisines=["North Indian", "Chinese"],
                avg_cost_for_two=700,
                rating=4.4,
                matched_features=["rating_threshold_match", "budget_fit"],
                heuristic_score=0.85
            ),
            Candidate(
                id="mock-3",
                name="Toit Brewpub",
                city="Bangalore",
                locality="Indiranagar",
                cuisines=["Italian", "Desserts"],
                avg_cost_for_two=1500,
                rating=4.7,
                matched_features=["cuisine_match", "rating_threshold_match"],
                heuristic_score=0.88
            )
        ]
        
    with st.spinner("Ranking candidates using LLM Orchestrator..."):
        try:
            items, summary = rank_with_llm_or_fallback(normalized, candidates)
        except Exception as e:
            st.error(f"LLM Orchestration error: {e}")
            st.stop()
            
    st.success(summary)
    
    for idx, item in enumerate(items):
        with st.expander(f"**{idx+1}. {item.restaurant_name}** ({item.rating} ⭐)"):
            st.write(f"**Cuisines:** {', '.join(item.cuisine)}")
            st.write(f"**Estimated Cost for Two:** ₹{item.estimated_cost_for_two}")
            st.write(f"**AI Insight:** {item.ai_explanation}")
