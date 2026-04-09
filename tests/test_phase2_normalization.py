from backend.models.schemas import RecommendationRequest
from backend.services.validators import normalize_request


def test_location_alias_normalization() -> None:
    payload = RecommendationRequest(
        location="blr",
        budget=1500.0,
        cuisines=[" italian ", "Italian", "chinese"],
        min_rating=4.0,
        additional_preferences="  quick service  ",
    )

    normalized = normalize_request(payload)

    assert normalized.location == "Bangalore"
    assert normalized.cuisines == ["Italian", "Chinese"]
    assert normalized.additional_preferences == "quick service"
