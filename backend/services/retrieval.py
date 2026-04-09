from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from psycopg import connect

from backend.config import load_backend_settings
from backend.models.schemas import RecommendationRequest

CANDIDATE_POOL_LIMIT = 30


@dataclass(frozen=True)
class Candidate:
    id: str
    name: str
    city: str
    locality: str | None
    cuisines: list[str]
    avg_cost_for_two: float
    rating: float
    matched_features: list[str]
    heuristic_score: float


def _budget_fit(cost: float, budget: float) -> float:
    return 1.0 if cost <= budget else 0.0


def _cuisine_match(candidate_cuisines: list[str], request_cuisines: list[str]) -> float:
    if not request_cuisines:
        return 1.0
    if not candidate_cuisines:
        return 0.0
    requested = {c.lower() for c in request_cuisines}
    present = {c.lower() for c in candidate_cuisines}
    overlap = len(requested.intersection(present))
    return overlap / max(1, len(requested))


def _location_proximity(city: str, locality: str | None, requested_location: str) -> float:
    req = requested_location.lower()
    if city.lower() == req:
        return 1.0
    if locality and locality.lower() == req:
        return 0.6
    return 0.0


def _matched_features(
    rating: float,
    cuisine_match_score: float,
    budget_fit_score: float,
    location_proximity_score: float,
    min_rating: float,
) -> list[str]:
    features: list[str] = []
    if location_proximity_score > 0:
        features.append("location_match")
    if budget_fit_score >= 1.0:
        features.append("budget_fit")
    if cuisine_match_score > 0:
        features.append("cuisine_match")
    if rating is not None and rating >= min_rating:
        features.append("rating_threshold_match")
    return features


def _heuristic_score(
    rating: float,
    cuisine_match_score: float,
    budget_fit_score: float,
    location_proximity_score: float,
) -> float:
    rating_score = rating / 5.0
    # Phase-3 scoring rule from architecture.
    return round(
        0.45 * rating_score
        + 0.30 * cuisine_match_score
        + 0.15 * budget_fit_score
        + 0.10 * location_proximity_score,
        6,
    )


def _fetch_base_rows(payload: RecommendationRequest) -> list[dict[str, Any]]:
    settings = load_backend_settings()
    if not settings.postgres_dsn:
        raise RuntimeError("POSTGRES_DSN is missing; cannot query restaurants.")

    # Exclude NULL cost and rating because we require valid cost/rating
    # based on user improvement request.
    budget_clause = "avg_cost_for_two IS NOT NULL AND avg_cost_for_two <= %s"
    params: list[Any] = [payload.budget]

    # Note: the dataset's `city` column often contains Bangalore localities (e.g., 'Whitefield', 'Btm').
    # Treat user `location` as a free-form "city or locality" query and match flexibly.
    location_pattern = f"%{payload.location.strip().lower()}%"

    query = f"""
        SELECT
            id::text,
            name,
            city,
            locality,
            cuisines,
            avg_cost_for_two::float8,
            rating::float8
        FROM restaurants
        WHERE
            (LOWER(city) LIKE %s OR LOWER(COALESCE(locality, '')) LIKE %s)
            AND rating IS NOT NULL AND rating >= %s
            AND {budget_clause}
        LIMIT 200
    """

    with connect(settings.postgres_dsn) as conn:
        with conn.cursor() as cur:
            # Replace exact-match params with LIKE patterns.
            params_with_location = [location_pattern, location_pattern, payload.min_rating] + params
            cur.execute(query, params_with_location)
            rows = cur.fetchall()

    output: list[dict[str, Any]] = []
    for row in rows:
        output.append(
            {
                "id": row[0],
                "name": row[1],
                "city": row[2],
                "locality": row[3],
                "cuisines": row[4] or [],
                "avg_cost_for_two": row[5],
                "rating": row[6],
            }
        )
    return output


def fetch_locations() -> list[str]:
    settings = load_backend_settings()
    if not settings.postgres_dsn:
        return []
    with connect(settings.postgres_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT city FROM restaurants WHERE city IS NOT NULL ORDER BY city ASC")
            rows = cur.fetchall()
            return [row[0] for row in rows]


def get_ranked_candidates(payload: RecommendationRequest) -> list[Candidate]:
    try:
        rows = _fetch_base_rows(payload)
    except RuntimeError:
        return []
    candidates: list[Candidate] = []

    for row in rows:
        cuisines = [str(c).strip() for c in row["cuisines"] if str(c).strip()]
        cuisine_match_score = _cuisine_match(cuisines, payload.cuisines)
        budget_fit_score = _budget_fit(row["avg_cost_for_two"], payload.budget)
        location_proximity_score = _location_proximity(
            row["city"],
            row["locality"],
            payload.location,
        )
        score = _heuristic_score(
            row["rating"],
            cuisine_match_score,
            budget_fit_score,
            location_proximity_score,
        )
        matched = _matched_features(
            row["rating"],
            cuisine_match_score,
            budget_fit_score,
            location_proximity_score,
            payload.min_rating,
        )
        candidates.append(
            Candidate(
                id=row["id"],
                name=row["name"],
                city=row["city"],
                locality=row["locality"],
                cuisines=cuisines,
                avg_cost_for_two=row["avg_cost_for_two"],
                rating=row["rating"],
                matched_features=matched,
                heuristic_score=score,
            )
        )

    candidates.sort(key=lambda item: (item.heuristic_score, item.rating or 0.0), reverse=True)
    return candidates[:CANDIDATE_POOL_LIMIT]
