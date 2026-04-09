from __future__ import annotations

import json

from backend.models.schemas import RecommendationRequest
from backend.services.retrieval import Candidate


def build_ranking_messages(
    payload: RecommendationRequest,
    candidates: list[Candidate],
) -> list[dict[str, str]]:
    candidate_rows = [
        {
            "restaurant_id": c.id,
            "name": c.name,
            "city": c.city,
            "locality": c.locality,
            "cuisines": c.cuisines,
            "avg_cost_for_two": c.avg_cost_for_two,
            "rating": c.rating,
            "heuristic_score": c.heuristic_score,
            "matched_features": c.matched_features,
        }
        for c in candidates
    ]

    system_text = (
        "You are a restaurant ranking assistant. Rank only from candidates provided. "
        "Do not invent restaurants. Return only JSON matching the schema described by the user."
    )
    user_text = (
        "User preferences:\n"
        f"{json.dumps(payload.model_dump(), ensure_ascii=True)}\n\n"
        "Candidates:\n"
        f"{json.dumps(candidate_rows, ensure_ascii=True)}\n\n"
        "Return JSON with keys: recommendations (array), summary (string).\n"
        "Each recommendation item must include: restaurant_id (string), rank (int starting from 1), "
        "fit_score (number 0-1), explanation (string <= 180 chars).\n"
        "Write a rich, conversational, engaging AI explanation for why each restaurant is recommended. "
        "Do not output raw heuristic scores. Focus on cuisine, ratings, and location.\n"
        "Use top candidates only and keep explanations concise."
    )
    return [
        {"role": "system", "content": system_text},
        {"role": "user", "content": user_text},
    ]
