# Phase 7 - Personalization and Optimization

## Purpose
Improve recommendation quality with user feedback and smarter ranking.

## Enhancements
- Feedback capture (`helpful`, `not_helpful`, clicked item)
- profile-aware reranking (if user history exists)
- embedding-based semantic matching for free-text preferences
- hybrid score:
  - deterministic fit score
  - LLM fit score
  - behavioral feedback boost

## Cost and Performance Optimization
- model routing (smaller model for easy cases, stronger model for complex intent)
- prompt compression for large candidate sets
- cache top-city popular sets for cold starts

## Exit Criteria
- measurable lift on relevance metrics.
- reduced average token cost.
- improved repeat-user engagement.
