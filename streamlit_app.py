import streamlit as st
import requests

st.set_page_config(page_title="Zomato AI Backend Tester", layout="wide")

st.title("Zomato AI Backend - Streamlit Deployment")
st.markdown("Use this interface to test the FastAPI backend directly via Streamlit.")

BACKEND_URL = "http://127.0.0.1:8000/v1"

with st.sidebar:
    st.header("Search Filters")
    try:
        res = requests.get(f"{BACKEND_URL}/locations", timeout=3)
        if res.ok and res.json():
            available_locations = res.json()
        else:
            available_locations = ["Bangalore", "Mumbai", "Delhi"]
    except Exception:
        available_locations = ["Bangalore", "Mumbai", "Delhi"]

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
    
    with st.spinner("Fetching recommendations from FastAPI..."):
        try:
            response = requests.post(f"{BACKEND_URL}/recommendations", json=payload_dict, timeout=30)
            if not response.ok:
                st.error(f"API Error: {response.text}")
                st.stop()
            
            data = response.json()
        except Exception as e:
            st.error(f"Failed to connect to FastAPI backend: {e}")
            st.stop()
            
    summary = data.get("summary", "Done.")
    items = data.get("recommendations", [])
    
    st.success(summary)
    
    if not items:
        st.warning("No candidates found matching your criteria.")
    else:
        for idx, item in enumerate(items):
            with st.expander(f"**{idx+1}. {item.get('restaurant_name')}** ({item.get('rating')} ⭐)"):
                cuisine_text = ", ".join(item.get("cuisine", []))
                st.write(f"**Cuisines:** {cuisine_text}")
                st.write(f"**Estimated Cost for Two:** ₹{item.get('estimated_cost_for_two')}")
                st.write(f"**AI Insight:** {item.get('ai_explanation')}")
