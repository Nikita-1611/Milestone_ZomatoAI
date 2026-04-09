from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

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
ROOT_DIR = Path(__file__).resolve().parent.parent
UI_FILE = ROOT_DIR / "frontend" / "index.html"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=FileResponse)
def ui() -> FileResponse:
    return FileResponse(UI_FILE)


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
