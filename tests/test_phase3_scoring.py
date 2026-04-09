from backend.services import retrieval


def test_heuristic_score_priority() -> None:
    better = retrieval._heuristic_score(
        rating=4.5,
        cuisine_match_score=1.0,
        budget_fit_score=1.0,
        location_proximity_score=1.0,
    )
    weaker = retrieval._heuristic_score(
        rating=3.0,
        cuisine_match_score=0.5,
        budget_fit_score=1.0,
        location_proximity_score=0.6,
    )
    assert better > weaker


def test_cuisine_match_no_request_defaults_to_one() -> None:
    assert retrieval._cuisine_match(["Italian"], []) == 1.0
