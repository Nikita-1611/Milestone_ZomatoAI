# Phase 1 - Data Ingestion and Canonical Modeling

## Purpose
Create a reliable restaurant dataset from Hugging Face source.

## Input
- Source dataset: `ManikaSaini/zomato-restaurant-recommendation`

## Pipeline Design
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

## Canonical Schema (PostgreSQL)
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

## Data Quality Rules
- Drop records with missing `name` or missing location hierarchy.
- Keep only ratings in expected range (for example 0-5).
- Mark uncertain values as `null`, not guessed values.

## Exit Criteria
- Re-runnable ingestion script is idempotent.
- Data quality report generated per run.
- Canonical table queryable with <200ms for basic filters on sample scale.
