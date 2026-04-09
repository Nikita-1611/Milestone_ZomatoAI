from backend.services.response_validator import parse_and_validate_ranking_response


def test_phase4_response_validator_accepts_valid_json() -> None:
    content = """
    {
      "recommendations": [
        {"restaurant_id":"id-1","rank":1,"fit_score":0.91,"explanation":"Great cuisine fit."},
        {"restaurant_id":"id-2","rank":2,"fit_score":0.82,"explanation":"Good rating and budget fit."}
      ],
      "summary":"Top picks are balanced for your preferences."
    }
    """
    parsed = parse_and_validate_ranking_response(content)
    assert parsed["recommendations"][0]["restaurant_id"] == "id-1"
