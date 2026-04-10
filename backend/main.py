from __future__ import annotations

from fastapi import FastAPI

from backend.models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
)
from backend.services.orchestrator import rank_with_llm_or_fallback
from backend.services.retrieval import get_ranked_candidates, fetch_locations
from backend.services.validators import normalize_request, validate_semantics

app = FastAPI(
    title="Zomato AI Recommendation API",
    version="0.1.0",
    description="Phase 4 backend with deterministic retrieval + LLM orchestration.",
)



@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "message": "Zomato AI API is live"}


@app.get("/v1/locations")
def locations() -> list[str]:
    return fetch_locations()


@app.post("/v1/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    validate_semantics(payload)
    normalized = normalize_request(payload)
    candidates = get_ranked_candidates(normalized)
    items, summary = rank_with_llm_or_fallback(normalized, candidates)
    return RecommendationResponse(
        location=normalized.location,
        recommendations=items,
        summary=summary,
    )
