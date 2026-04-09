from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    location: str = Field(..., min_length=2, description="City or locality name.")
    budget: float = Field(..., gt=0.0, description="Numerical budget constraint for cost for two.")
    cuisines: list[str] = Field(default_factory=list, max_length=5)
    min_rating: float = Field(0.0, ge=0.0, le=5.0)
    additional_preferences: str | None = Field(default=None, max_length=300)

    @field_validator("cuisines")
    @classmethod
    def validate_cuisines(cls, values: list[str]) -> list[str]:
        cleaned = [v.strip() for v in values if v and v.strip()]
        if len(cleaned) > 5:
            raise ValueError("At most 5 cuisines are allowed.")
        return cleaned


class RecommendationItem(BaseModel):
    restaurant_name: str
    cuisine: list[str]
    rating: float
    estimated_cost_for_two: float
    ai_explanation: str


class RecommendationResponse(BaseModel):
    location: str
    recommendations: list[RecommendationItem]
    summary: str
