# Phase 4 - LLM Ranking and Explanation Orchestration

## Purpose
Use LLM to rank candidates and produce natural, user-friendly explanations.

## Orchestration Components
- `prompt_builder`
  - creates system and user prompts.
  - injects candidate list as structured context.
- `llm_client`
  - provider abstraction (easy model swap).
- `response_validator`
  - validates JSON schema and ranking integrity.
- `fallback_handler`
  - deterministic ranking if LLM fails/timeouts.

## Prompt Design Pattern
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

## Expected LLM Output (Example)
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

## Guardrails
- JSON schema validation and re-try with repair prompt.
- Hard cap on candidates/tokens.
- Timeout with deterministic fallback.
- Content filtering for unsafe or irrelevant output.

## Exit Criteria
- LLM output success rate target met (for example >98% valid JSON after retry).
- Hallucination checks pass (all IDs map to known candidates).
- Average generation latency within target budget.
