# Phase 5 - Response Assembly and User Experience

## Purpose
Deliver recommendation output in a clean and explainable format.

## Response Contract
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
      "ai_explanation": "Great cuisine match and aligns with your medium budget."
    }
  ],
  "summary": "These options best match your cuisine and rating preferences."
}
```

## UX Features
- Input form with inline validation
- Recommendation cards with:
  - name
  - cuisine tags
  - rating badge
  - cost indicator
  - explanation text
- Empty state handling:
  - "No exact matches" + broadened alternatives

## Exit Criteria
- End-to-end flow from input to render works.
- Graceful handling for no-result and LLM-fallback scenarios.
- Basic accessibility and responsive behavior validated.
