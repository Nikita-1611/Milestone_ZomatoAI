from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    postgres_dsn: str
    hf_dataset_name: str
    raw_ingestion_dir: str


def load_settings() -> Settings:
    load_dotenv()
    dsn = os.getenv("POSTGRES_DSN", "").strip()
    if not dsn:
        raise ValueError("POSTGRES_DSN is required. Add it to your environment or .env file.")

    return Settings(
        postgres_dsn=dsn,
        hf_dataset_name=os.getenv(
            "HF_DATASET_NAME",
            "ManikaSaini/zomato-restaurant-recommendation",
        ),
        raw_ingestion_dir=os.getenv("RAW_INGESTION_DIR", "data_pipeline/raw_ingestions"),
    )
