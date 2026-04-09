from __future__ import annotations

from fastapi import HTTPException, status

from backend.models.schemas import RecommendationRequest
from backend.services.normalizers import (
    normalize_additional_preferences,
    normalize_cuisines,
    normalize_location,
)


def validate_semantics(payload: RecommendationRequest) -> None:
    if payload.min_rating < 0 or payload.min_rating > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_rating must be in range [0, 5].",
        )


def normalize_request(payload: RecommendationRequest) -> RecommendationRequest:
    return RecommendationRequest(
        location=normalize_location(payload.location),
        budget=payload.budget,
        cuisines=normalize_cuisines(payload.cuisines),
        min_rating=payload.min_rating,
        additional_preferences=normalize_additional_preferences(payload.additional_preferences),
    )
