from __future__ import annotations

import json


class LLMResponseValidationError(Exception):
    pass


def parse_and_validate_ranking_response(content: str) -> dict:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMResponseValidationError("LLM output is not valid JSON.") from exc

    recommendations = parsed.get("recommendations")
    summary = parsed.get("summary")
    if not isinstance(recommendations, list):
        raise LLMResponseValidationError("recommendations must be a list.")
    if not isinstance(summary, str):
        raise LLMResponseValidationError("summary must be a string.")

    seen_ranks: set[int] = set()
    for idx, item in enumerate(recommendations):
        if not isinstance(item, dict):
            raise LLMResponseValidationError(f"recommendation at index {idx} is not an object.")
        required = {"restaurant_id", "rank", "fit_score", "explanation"}
        if not required.issubset(item.keys()):
            raise LLMResponseValidationError(f"recommendation at index {idx} missing required fields.")
        if not isinstance(item["restaurant_id"], str):
            raise LLMResponseValidationError("restaurant_id must be string.")
        if not isinstance(item["rank"], int) or item["rank"] < 1:
            raise LLMResponseValidationError("rank must be a positive integer.")
        if item["rank"] in seen_ranks:
            raise LLMResponseValidationError("rank values must be unique.")
        seen_ranks.add(item["rank"])
        if not isinstance(item["fit_score"], (int, float)):
            raise LLMResponseValidationError("fit_score must be numeric.")
        if not (0 <= float(item["fit_score"]) <= 1):
            raise LLMResponseValidationError("fit_score must be between 0 and 1.")
        if not isinstance(item["explanation"], str) or not item["explanation"].strip():
            raise LLMResponseValidationError("explanation must be non-empty string.")
    return parsed
