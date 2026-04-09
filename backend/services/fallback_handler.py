from __future__ import annotations

from backend.models.schemas import RecommendationItem
from backend.services.retrieval import Candidate


def build_deterministic_fallback(
    candidates: list[Candidate],
    top_k: int,
) -> tuple[list[RecommendationItem], str]:
    top = candidates[:top_k]
    items: list[RecommendationItem] = []
    for candidate in top:
        reasons = ", ".join(candidate.matched_features) if candidate.matched_features else "base filters"
        items.append(
            RecommendationItem(
                restaurant_name=candidate.name,
                cuisine=candidate.cuisines,
                rating=candidate.rating,
                estimated_cost_for_two=candidate.avg_cost_for_two,
                ai_explanation=(
                    f"Fallback ranking from deterministic engine with score "
                    f"{candidate.heuristic_score:.3f} ({reasons})."
                ),
            )
        )
    return items, "Served deterministic fallback because LLM response was unavailable or invalid."
