from backend.models.schemas import RecommendationRequest
from backend.services.prompt_builder import build_ranking_messages
from backend.services.retrieval import Candidate


def test_phase4_prompt_includes_candidate_and_constraints() -> None:
    payload = RecommendationRequest(
        location="Bangalore",
        budget=1500.0,
        cuisines=["Italian"],
        min_rating=4.0,
        additional_preferences="family friendly",
    )
    candidates = [
        Candidate(
            id="r1",
            name="Pasta Hub",
            city="Bangalore",
            locality="Indiranagar",
            cuisines=["Italian"],
            avg_cost_for_two=1400.0,
            rating=4.4,
            matched_features=["location_match"],
            heuristic_score=0.9,
        )
    ]
    messages = build_ranking_messages(payload, candidates)
    assert len(messages) == 2
    assert "Do not invent restaurants" in messages[0]["content"]
    assert "restaurant_id" in messages[1]["content"]
