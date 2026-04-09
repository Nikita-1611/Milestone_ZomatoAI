from __future__ import annotations

import re

LOCATION_ALIASES = {
    "blr": "Bangalore",
    "bangalore urban": "Bangalore",
    "bengaluru": "Bangalore",
    "delhi ncr": "Delhi",
    "new delhi": "Delhi",
    "bombay": "Mumbai",
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_location(location: str) -> str:
    key = normalize_text(location).lower()
    mapped = LOCATION_ALIASES.get(key, key)
    return mapped.title()


def normalize_cuisines(cuisines: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for item in cuisines:
        normalized = normalize_text(item).title()
        key = normalized.lower()
        if key not in seen:
            output.append(normalized)
            seen.add(key)
    return output


def normalize_additional_preferences(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = normalize_text(value)
    return cleaned or None
