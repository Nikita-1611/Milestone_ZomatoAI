# Phase 1 Data Pipeline

This folder contains the Phase 1 implementation:
- dataset ingestion from Hugging Face,
- normalization and quality filtering,
- canonical PostgreSQL schema and upsert loading,
- ingestion run metadata and quality reports.

## Prerequisites

- Python 3.10+
- Running PostgreSQL database

## Setup

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Create environment file:
   - copy `.env.example` to `.env`
3. Update `POSTGRES_DSN` in `.env`.

## Run ingestion

From repository root:

- `python -m data_pipeline.ingest_zomato`

## Outputs

- Canonical tables:
  - `restaurants`
  - `ingestion_runs`
- Raw snapshot:
  - `data_pipeline/raw_ingestions/<timestamp>/raw_snapshot.jsonl`
- Data quality reports:
  - `data_pipeline/reports/quality_report_<timestamp>.json`
  - `data_pipeline/reports/quality_report_<timestamp>.csv`

## Idempotency

Records are upserted using `source_hash` as a stable key, so reruns update existing rows instead of duplicating data.
