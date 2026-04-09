# Phase 1 Implementation Notes

Phase 1 has been implemented with:

- **Dataset ingestion** from Hugging Face dataset `ManikaSaini/zomato-restaurant-recommendation`
- **Preprocessing and normalization** for key fields:
  - `name`
  - `city`
  - `locality`
  - `cuisines`
  - `avg_cost_for_two`
  - `rating`
- **Data quality rules**:
  - drop rows without `name` or `city`
  - drop rows with invalid rating range
  - deduplicate using deterministic `source_hash`
- **Canonical schema** in PostgreSQL:
  - `restaurants`
  - `ingestion_runs`
- **Idempotent load** using upsert on `source_hash`
- **Run reports** for row counts, dropped records, and snapshot location

## Files Added

- `requirements.txt`
- `.env.example`
- `data_pipeline/config.py`
- `data_pipeline/schema.sql`
- `data_pipeline/ingest_zomato.py`
- `data_pipeline/README.md`

## How to Execute

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Configure `.env` from `.env.example`
3. Run:
   - `python -m data_pipeline.ingest_zomato`
