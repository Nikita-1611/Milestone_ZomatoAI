# Phase 0 - Project Foundation and Standards

## Purpose
Establish repository structure, coding standards, and baseline runtime.

## Components
- `frontend/` (React or Next.js)
- `backend/` (FastAPI)
- `data/` (ingestion, preprocessing, transformation scripts)
- `infra/` (docker, compose, deployment manifests)
- `docs/` (problem statement, architecture, runbooks)

## Engineering Baseline
- Environment variables with `.env.example`
- Unified formatting/linting (`ruff` + `black` for Python, `eslint` + `prettier` for JS/TS)
- Basic test runners (`pytest`, frontend unit tests)
- Pre-commit hooks for lint + unit checks

## Exit Criteria
- Repo boots locally with one command (`docker compose up` or equivalent)
- Health endpoint available (`GET /health`)
- CI runs lint + tests on pull request
