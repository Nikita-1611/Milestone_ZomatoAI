# Phase 6 - Observability, Evaluation, and Reliability

## Purpose
Make the system production-safe and measurable.

## Observability
- **Logs**: request_id, filters applied, candidate count, model used, fallback usage.
- **Metrics**:
  - request count, success/failure rate
  - p50/p95 latency (retrieval, LLM, total)
  - token usage and cost per request
- **Tracing**:
  - spans for retrieval, prompt build, model call, parsing

## Quality Evaluation
- Offline evaluation dataset of user scenarios.
- Metrics:
  - relevance@k
  - constraint satisfaction rate
  - explanation quality review score (human rubric)

## Reliability Controls
- circuit breaker for LLM provider failures
- retry policy with exponential backoff
- cached response for repeated identical queries

## Exit Criteria
- Dashboards for latency/error/cost are live.
- SLOs defined and monitored.
- Fallback path tested and documented.
