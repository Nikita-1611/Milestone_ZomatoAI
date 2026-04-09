import streamlit as st
import json

from backend.models.schemas import RecommendationRequest
from backend.services.orchestrator import rank_with_llm_or_fallback
from backend.services.retrieval import get_ranked_candidates, fetch_locations
from backend.services.validators import normalize_request, validate_semantics

st.set_page_config(page_title="Zomato AI Backend Tester", layout="wide")

st.title("Zomato AI Backend - Streamlit Deployment")
st.markdown("Use this interface to test the backend logic directly via Streamlit.")

with st.sidebar:
    st.header("Search Filters")
    try:
        available_locations = fetch_locations()
        if not available_locations:
            available_locations = ["Bangalore", "Mumbai", "Delhi"]
            st.warning("DB returned no locations. Using fallback locations.")
    except Exception as e:
        available_locations = ["Bangalore", "Mumbai", "Delhi"]
        st.error(f"Failed to fetch locations from DB: {e}")

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
    
    with st.spinner("Fetching candidates from database..."):
        try:
            candidates = get_ranked_candidates(normalized)
            st.info(f"Retrieved {len(candidates)} candidates from the database.")
        except Exception as e:
            st.error(f"Database error: {e}")
            st.stop()
            
    if not candidates:
        st.warning("No candidates found matching your criteria.")
        st.stop()
        
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
