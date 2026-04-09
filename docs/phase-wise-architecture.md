# AI-Powered Restaurant Recommendation System
## Detailed Phase-Wise Architecture

This document expands the problem statement into an execution-ready architecture plan.  
Scope: recommendation system using structured restaurant data + LLM reasoning.

---

## 1) Target System Overview

### Core Objective
Build a service that:
- accepts user preferences (location, budget, cuisine, minimum rating, optional text preferences),
- retrieves best-fit restaurant candidates from structured data,
- uses an LLM to rank and explain recommendations,
- returns a clear user-facing response.

### High-Level Building Blocks
- **Frontend**: preference capture + recommendation display.
- **Backend API**: request validation, candidate retrieval, orchestration, response shaping.
- **Data Pipeline**: ingest and clean Hugging Face Zomato dataset.
- **Primary Data Store**: PostgreSQL for restaurant records and metadata.
- **Caching Layer**: Redis for hot queries and response caching (optional in early phases).
- **LLM Provider**: external model endpoint for ranking + explanation generation.
- **Observability**: logs, metrics, traces, quality evaluation artifacts.

---

## 2) Phase 0 - Project Foundation and Standards

### Purpose
Establish repository structure, coding standards, and baseline runtime.

### Components
- `frontend/` (React or Next.js)
- `backend/` (FastAPI)
- `data/` (ingestion, preprocessing, transformation scripts)
- `infra/` (docker, compose, deployment manifests)
- `docs/` (problem statement, architecture, runbooks)

### Engineering Baseline
- Environment variables with `.env.example`
- Unified formatting/linting (`ruff` + `black` for Python, `eslint` + `prettier` for JS/TS)
- Basic test runners (`pytest`, frontend unit tests)
- Pre-commit hooks for lint + unit checks

### Exit Criteria
- Repo boots locally with one command (`docker compose up` or equivalent)
- Health endpoint available (`GET /health`)
- CI runs lint + tests on pull request

---

## 3) Phase 1 - Data Ingestion and Canonical Modeling

### Purpose
Create a reliable restaurant dataset from Hugging Face source.

### Input
- Source dataset: `ManikaSaini/zomato-restaurant-recommendation`

### Pipeline Design
1. **Extract**
   - Pull latest dataset snapshot.
   - Persist raw file in a versioned `raw_ingestions` area.
2. **Transform**
   - Normalize location spellings and casing.
   - Standardize cuisines into array form.
   - Parse cost into numeric representation.
   - Parse rating to `float` and filter invalid/outlier values.
   - Deduplicate by stable key (`name + location + address`, if available).
3. **Load**
   - Upsert cleaned records into canonical table.
   - Save ingestion metadata (row count, run id, timestamp, failures).

### Canonical Schema (PostgreSQL)
- `restaurants`
  - `id` (uuid, pk)
  - `name` (text, indexed)
  - `city` (text, indexed)
  - `locality` (text, indexed, nullable)
  - `cuisines` (text[], gin index)
  - `avg_cost_for_two` (numeric, indexed)
  - `rating` (numeric, indexed)
  - `tags` (text[], nullable)
  - `source_hash` (text, unique)
  - `created_at`, `updated_at`
- `ingestion_runs`
  - `run_id`, `status`, `source_version`, `row_count`, `error_count`, `started_at`, `completed_at`

### Data Quality Rules
- Drop records with missing `name` or missing location hierarchy.
- Keep only ratings in expected range (for example 0-5).
- Mark uncertain values as `null`, not guessed values.

### Exit Criteria
- Re-runnable ingestion script is idempotent.
- Data quality report generated per run.
- Canonical table queryable with <200ms for basic filters on sample scale.

---

## 4) Phase 2 - User Preference Contract and API Surface

### Purpose
Create stable input contracts for recommendation requests.

### Request Contract
`POST /v1/recommendations`

```json
{
  "location": "Bangalore",
  "budget": 1500.0,
  "cuisines": ["Italian", "Continental"],
  "min_rating": 4.0,
  "additional_preferences": "family-friendly and quick service"
}
```

### Validation Rules
- `location`: required, non-empty, minimum 2 chars
- `budget`: floating-point numeric limit constraint
- `cuisines`: optional array, max 5 entries
- `min_rating`: `0 <= min_rating <= 5`
- `additional_preferences`: optional, max length guard (for token safety)

### Backend Modules
- `schemas.py`: Pydantic request/response models
- `validators.py`: semantic input validation
- `normalizers.py`: trim, canonicalize, map aliases (`blr` -> `Bangalore`)

### Exit Criteria
- Invalid payloads produce clear 4xx responses.
- API contract documented in OpenAPI.
- Input normalization unit tests pass.

---

## 5) Phase 3 - Deterministic Retrieval and Candidate Generation

### Purpose
Retrieve high-quality candidates before LLM ranking.

### Why This Layer Is Mandatory
- Reduces hallucinations by grounding LLM in real data.
- Controls cost by limiting prompt size.
- Improves consistency and latency.

### Retrieval Flow
1. **Location filtering**
   - city exact match, then locality fallback.
2. **Budget mapping**
   - numeric ceiling enforced against estimated cost.
3. **Cuisine matching**
   - case-insensitive overlap with normalized cuisine list.
4. **Minimum rating filter**
   - strict threshold enforcement. Drop records with missing (NULL) values for both ratings and average cost for two.
5. **Heuristic pre-score**
   - weighted score to reduce candidate set (e.g., top 30).

### Pre-Score Example
- `score = 0.45*rating + 0.30*cuisine_match + 0.15*budget_fit + 0.10*location_proximity`

### Output Contract (Internal)
Each candidate includes:
- id, name, city/locality
- cuisines
- avg_cost_for_two
- rating
- matched_features (for explanation grounding)
- heuristic_score

### Exit Criteria
- Retrieval endpoint returns candidates in predictable order.
- Rule-based tests for edge cases (no cuisine, tight budget, sparse city data).
- p95 retrieval latency target met (for example <300ms).

### LLM Provider Decision for this Project
- Use **Groq LLM** starting from this phase's implementation path.
- Store the API key in `.env` (for example `GROQ_API_KEY=...`) and load it via environment variables in backend services.

---

## 6) Phase 4 - LLM Ranking and Explanation Orchestration

### Purpose
Use LLM to rank candidates and produce natural, user-friendly explanations.

### Orchestration Components
- `prompt_builder`
  - creates system and user prompts.
  - injects candidate list as structured context.
- `llm_client`
  - provider abstraction (easy model swap).
- `response_validator`
  - validates JSON schema and ranking integrity.
- `fallback_handler`
  - deterministic ranking if LLM fails/timeouts.

### Prompt Design Pattern
- **System instructions**:
  - rank only from provided candidates.
  - do not invent restaurants.
  - keep explanations concise and preference-aware.
- **User context**:
  - explicit preferences and constraints.
- **Candidate payload**:
  - structured rows with key fields.
- **Expected output**:
  - strict JSON schema with rank and explanation.

### Expected LLM Output (Example)
```json
{
  "recommendations": [
    {
      "restaurant_id": "uuid-1",
      "rank": 1,
      "fit_score": 0.93,
      "explanation": "Matches your Italian preference, fits medium budget, and has strong ratings."
    }
  ],
  "summary": "Top picks balance cuisine match and value in Bangalore."
}
```

### Guardrails
- JSON schema validation and re-try with repair prompt.
- Hard cap on candidates/tokens.
- Timeout with deterministic fallback.
- Content filtering for unsafe or irrelevant output.

### Exit Criteria
- LLM output success rate target met (for example >98% valid JSON after retry).
- Hallucination checks pass (all IDs map to known candidates).
- Average generation latency within target budget.

### Implementation Order Note
- Implement **backend Phase 4 first** (prompt builder, Groq client, response validator, fallback handler, orchestration).
- Implement **frontend website integration later** after backend APIs are stable.

---

## 7) Phase 5 - Response Assembly and User Experience

### Purpose
Deliver recommendation output in a clean and explainable format.

### Response Contract
`200 OK`
```json
{
  "request_id": "req_123",
  "location": "Bangalore",
  "recommendations": [
    {
      "restaurant_name": "Sample Bistro",
      "cuisine": ["Italian", "Continental"],
      "rating": 4.4,
      "estimated_cost_for_two": 1400,
      "ai_explanation": "Great cuisine match and aligns with your budget."
    }
  ],
  "summary": "These options best match your cuisine and rating preferences."
}
```

### UX Features
- Input form with inline validation
- Recommendation cards with:
  - name
  - cuisine tags
  - rating badge
  - cost indicator
  - explanation text
- Empty state handling:
  - "No exact matches" + broadened alternatives

### Exit Criteria
- End-to-end flow from input to render works.
- Graceful handling for no-result and LLM-fallback scenarios.
- Basic accessibility and responsive behavior validated.

---

## 8) Phase 6 - Observability, Evaluation, and Reliability

### Purpose
Make the system production-safe and measurable.

### Observability
- **Logs**: request_id, filters applied, candidate count, model used, fallback usage.
- **Metrics**:
  - request count, success/failure rate
  - p50/p95 latency (retrieval, LLM, total)
  - token usage and cost per request
- **Tracing**:
  - spans for retrieval, prompt build, model call, parsing

### Quality Evaluation
- Offline evaluation dataset of user scenarios.
- Metrics:
  - relevance@k
  - constraint satisfaction rate
  - explanation quality review score (human rubric)

### Reliability Controls
- circuit breaker for LLM provider failures
- retry policy with exponential backoff
- cached response for repeated identical queries

### Exit Criteria
- Dashboards for latency/error/cost are live.
- SLOs defined and monitored.
- Fallback path tested and documented.

---

## 9) Phase 7 - Personalization and Optimization

### Purpose
Improve recommendation quality with user feedback and smarter ranking.

### Enhancements
- Feedback capture (`helpful`, `not_helpful`, clicked item)
- profile-aware reranking (if user history exists)
- embedding-based semantic matching for free-text preferences
- hybrid score:
  - deterministic fit score
  - LLM fit score
  - behavioral feedback boost

### Cost and Performance Optimization
- model routing (smaller model for easy cases, stronger model for complex intent)
- prompt compression for large candidate sets
- cache top-city popular sets for cold starts

### Exit Criteria
- measurable lift on relevance metrics.
- reduced average token cost.
- improved repeat-user engagement.

---

## 10) Cross-Cutting Concerns

### Security and Privacy
- No sensitive user data in logs.
- API keys stored in secrets manager.
- Rate limiting and abuse protection.

### Configuration Management
- Versioned budget bands and ranking weights.
- Prompt template version tracking.
- Feature flags for rollout (LLM ranking, fallback policy).

### Testing Strategy
- Unit: validators, filters, scoring, prompt builders.
- Integration: API + DB + mocked LLM.
- End-to-end: sample user journeys.
- Regression: frozen scenarios to detect ranking drift.

---

## 11) Suggested Delivery Timeline (Illustrative)

- **Sprint 1**: Phases 0-1 (foundation + data pipeline)
- **Sprint 2**: Phases 2-3 (API contracts + deterministic retrieval)
- **Sprint 3**: Phases 4-5 (LLM orchestration + UX integration)
- **Sprint 4**: Phase 6 (observability, eval, reliability hardening)
- **Sprint 5+**: Phase 7 (personalization and optimization)

---

## 12) Deployment Architecture

### Frontend Deployment
- **Platform**: Vercel
- **Why**: Native support for Next.js, zero-config CI/CD from GitHub, edge caching, and scalable serverless compute for UI rendering.

### Backend Deployment
- **Platform**: Streamlit (Community Cloud / Enterprise)
- **Why**: Quick iteration, built-in data visualization capabilities if internal dashboards are needed, and streamlined hosting for Python apps.
- **Note**: While Streamlit is traditionally a UI framework, it can serve as a unified backend-frontend for data apps or act as a wrapper around the FastAPI logic if deployed in a Python-centric ecosystem.

---

## 13) Minimum Viable Production Cut (MVP)

For fastest launch, include:
- canonical dataset ingestion,
- validated recommendation API,
- deterministic candidate retrieval,
- LLM ranking with strict fallback,
- recommendation UI with explanation cards,
- baseline metrics and logging.

This MVP is enough to validate product usefulness while preserving a clear path to scale.
