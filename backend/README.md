# Backend Phase 2

Implements Phase 2 from architecture:
- request/response schemas,
- validation rules,
- normalization layer,
- `POST /v1/recommendations` API contract.

Phase 3 update:
- deterministic retrieval from PostgreSQL
- budget/location/cuisine/rating filtering
- heuristic pre-scoring and top candidate selection

## Run locally

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Start API:
   - `uvicorn backend.main:app --reload`
3. Open docs:
   - `http://127.0.0.1:8000/docs`

## Implemented modules

- `backend/models/schemas.py`
- `backend/services/normalizers.py`
- `backend/services/validators.py`
- `backend/main.py`
- `backend/services/retrieval.py`
