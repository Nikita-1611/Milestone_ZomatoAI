from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class BackendSettings:
    postgres_dsn: str
    groq_api_key: str | None
    groq_model: str


def load_backend_settings() -> BackendSettings:
    load_dotenv()
    return BackendSettings(
        postgres_dsn=os.getenv("POSTGRES_DSN", "").strip(),
        groq_api_key=os.getenv("GROQ_API_KEY", "").strip() or None,
        groq_model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip(),
    )
