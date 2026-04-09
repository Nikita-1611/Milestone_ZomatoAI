from __future__ import annotations

from backend.models.schemas import RecommendationItem, RecommendationRequest
from backend.services.fallback_handler import build_deterministic_fallback
from backend.services.llm_client import LLMClientError, run_groq_chat
from backend.services.prompt_builder import build_ranking_messages
from backend.services.response_validator import (
    LLMResponseValidationError,
    parse_and_validate_ranking_response,
)
from backend.services.retrieval import Candidate

DEFAULT_TOP_K = 5

def _map_llm_result_to_items(
    llm_ranked: list[dict],
    candidates_by_id: dict[str, Candidate],
    top_k: int,
) -> list[RecommendationItem]:
    llm_ranked = sorted(llm_ranked, key=lambda item: item["rank"])
    items: list[RecommendationItem] = []
    for item in llm_ranked:
        candidate = candidates_by_id.get(item["restaurant_id"])
        if not candidate:
            continue
        items.append(
            RecommendationItem(
                restaurant_name=candidate.name,
                cuisine=candidate.cuisines,
                rating=candidate.rating,
                estimated_cost_for_two=candidate.avg_cost_for_two,
                ai_explanation=item["explanation"].strip(),
            )
        )
        if len(items) >= top_k:
            break
    return items


def rank_with_llm_or_fallback(
    payload: RecommendationRequest,
    candidates: list[Candidate],
) -> tuple[list[RecommendationItem], str]:
    if not candidates:
        return [], "No matching candidates found for the provided preferences."

    messages = build_ranking_messages(payload, candidates)
    candidates_by_id = {c.id: c for c in candidates}
    try:
        content = run_groq_chat(messages)
        parsed = parse_and_validate_ranking_response(content)
        mapped = _map_llm_result_to_items(parsed["recommendations"], candidates_by_id, DEFAULT_TOP_K)
        if mapped:
            return mapped, parsed["summary"]

        # Parsed response was valid but didn't map to known candidate IDs.
        return build_deterministic_fallback(candidates, DEFAULT_TOP_K)
    except (LLMClientError, LLMResponseValidationError):
        # One repair attempt with tighter instruction.
        repair_messages = messages + [
            {
                "role": "user",
                "content": (
                    "Your previous output was invalid. Return only strict JSON with keys "
                    "recommendations and summary, and use only provided restaurant_id values."
                ),
            }
        ]
        try:
            repaired = run_groq_chat(repair_messages)
            parsed = parse_and_validate_ranking_response(repaired)
            mapped = _map_llm_result_to_items(parsed["recommendations"], candidates_by_id, DEFAULT_TOP_K)
            if mapped:
                return mapped, parsed["summary"]
        except (LLMClientError, LLMResponseValidationError):
            pass
        return build_deterministic_fallback(candidates, DEFAULT_TOP_K)
