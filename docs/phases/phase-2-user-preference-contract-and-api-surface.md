# Phase 2 - User Preference Contract and API Surface

## Purpose
Create stable input contracts for recommendation requests.

## Request Contract
`POST /v1/recommendations`

```json
{
  "location": "Bangalore",
  "budget": "medium",
  "cuisines": ["Italian", "Continental"],
  "min_rating": 4.0,
  "additional_preferences": "family-friendly and quick service",
  "top_k": 5
}
```

## Validation Rules
- `location`: required, non-empty, minimum 2 chars
- `budget`: one of `low|medium|high`
- `cuisines`: optional array, max 5 entries
- `min_rating`: `0 <= min_rating <= 5`
- `top_k`: default 5, max 10
- `additional_preferences`: optional, max length guard (for token safety)

## Backend Modules
- `schemas.py`: Pydantic request/response models
- `validators.py`: semantic input validation
- `normalizers.py`: trim, canonicalize, map aliases (`blr` -> `Bangalore`)

## Exit Criteria
- Invalid payloads produce clear 4xx responses.
- API contract documented in OpenAPI.
- Input normalization unit tests pass.
