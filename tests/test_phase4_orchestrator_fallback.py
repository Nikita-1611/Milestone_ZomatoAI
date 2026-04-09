from backend.models.schemas import RecommendationRequest
from backend.services.llm_client import LLMClientError
from backend.services.orchestrator import rank_with_llm_or_fallback
from backend.services.retrieval import Candidate


def test_phase4_orchestrator_uses_fallback_when_llm_unavailable(monkeypatch) -> None:
    payload = RecommendationRequest(
        location="Bangalore",
        budget=1500.0,
        cuisines=["Italian"],
        min_rating=4.0,
        additional_preferences=None,
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
            matched_features=["location_match", "cuisine_match", "budget_fit"],
            heuristic_score=0.91,
        ),
        Candidate(
            id="r2",
            name="Noodle Spot",
            city="Bangalore",
            locality="Koramangala",
            cuisines=["Chinese"],
            avg_cost_for_two=1100.0,
            rating=4.1,
            matched_features=["location_match", "budget_fit"],
            heuristic_score=0.76,
        ),
    ]

    def raise_error(_messages, max_tokens=500):  # noqa: ARG001
        raise LLMClientError("simulated")

    monkeypatch.setattr("backend.services.orchestrator.run_groq_chat", raise_error)
    items, summary = rank_with_llm_or_fallback(payload, candidates)
    assert len(items) == 2
    assert "fallback" in summary.lower()
