CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS ingestion_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status TEXT NOT NULL,
    source_version TEXT NOT NULL,
    row_count INTEGER NOT NULL DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    locality TEXT,
    cuisines TEXT[] NOT NULL DEFAULT '{}',
    avg_cost_for_two NUMERIC,
    rating NUMERIC,
    tags TEXT[] NOT NULL DEFAULT '{}',
    source_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_restaurants_name ON restaurants (name);
CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants (city);
CREATE INDEX IF NOT EXISTS idx_restaurants_locality ON restaurants (locality);
CREATE INDEX IF NOT EXISTS idx_restaurants_cost ON restaurants (avg_cost_for_two);
CREATE INDEX IF NOT EXISTS idx_restaurants_rating ON restaurants (rating);
CREATE INDEX IF NOT EXISTS idx_restaurants_cuisines_gin ON restaurants USING GIN (cuisines);
