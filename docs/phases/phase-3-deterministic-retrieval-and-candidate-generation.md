# Phase 3 - Deterministic Retrieval and Candidate Generation

## Purpose
Retrieve high-quality candidates before LLM ranking.

## Why This Layer Is Mandatory
- Reduces hallucinations by grounding LLM in real data.
- Controls cost by limiting prompt size.
- Improves consistency and latency.

## Retrieval Flow
1. **Location filtering**
   - city exact match, then locality fallback.
2. **Budget mapping**
   - `low`, `medium`, `high` mapped to configured cost ranges.
3. **Cuisine matching**
   - case-insensitive overlap with normalized cuisine list.
4. **Minimum rating filter**
   - strict threshold enforcement.
5. **Heuristic pre-score**
   - weighted score to reduce candidate set (e.g., top 30).

## Pre-Score Example
- `score = 0.45*rating + 0.30*cuisine_match + 0.15*budget_fit + 0.10*location_proximity`

## Output Contract (Internal)
Each candidate includes:
- id, name, city/locality
- cuisines
- avg_cost_for_two
- rating
- matched_features (for explanation grounding)
- heuristic_score

## Exit Criteria
- Retrieval endpoint returns candidates in predictable order.
- Rule-based tests for edge cases (no cuisine, tight budget, sparse city data).
- p95 retrieval latency target met (for example <300ms).
