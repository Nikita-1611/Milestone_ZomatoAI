from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from datasets import load_dataset
from psycopg import Connection, connect

from data_pipeline.config import load_settings


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _title_case(text: str) -> str:
    return text.title() if text else ""


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = _normalize_text(value)
    if not text:
        return None
    match = re.search(r"(\d+(\.\d+)?)", text)
    if not match:
        return None
    return float(match.group(1))


def _parse_cost(value: Any) -> float | None:
    if value is None:
        return None
    text = _normalize_text(value).lower().replace(",", "")
    if not text:
        return None
    nums = [float(m[0]) for m in re.findall(r"(\d+(\.\d+)?)", text)]
    if not nums:
        return None
    return max(nums)


def _parse_cuisines(value: Any) -> list[str]:
    text = _normalize_text(value)
    if not text:
        return []
    candidates = re.split(r"[,/|]", text)
    items: list[str] = []
    for part in candidates:
        cuisine = _title_case(_normalize_text(part))
        if cuisine and cuisine not in items:
            items.append(cuisine)
    return items


def _build_source_hash(name: str, city: str, locality: str, cuisines: list[str]) -> str:
    stable = f"{name}|{city}|{locality}|{','.join(cuisines)}"
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _pick_first(record: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in record and record[key] is not None:
            value = record[key]
            if _normalize_text(value):
                return value
    return None


def normalize_record(record: dict[str, Any]) -> dict[str, Any] | None:
    name = _normalize_text(_pick_first(record, ["Restaurant Name", "name", "restaurant_name"]))
    city = _title_case(_normalize_text(_pick_first(record, ["City", "city", "location"])))
    locality = _title_case(_normalize_text(_pick_first(record, ["Locality", "locality", "address"])))
    cuisines = _parse_cuisines(_pick_first(record, ["Cuisines", "cuisines", "Cuisine", "cuisine"]))
    rating = _parse_float(_pick_first(record, ["Aggregate rating", "rating", "user_rating", "rate"]))
    cost = _parse_cost(_pick_first(record, ["Average Cost for two", "average_cost_for_two", "cost_for_two", "approx_cost(for two people)"]))

    if not name or not city:
        return None
    if rating is not None and not (0.0 <= rating <= 5.0):
        return None

    return {
        "name": name,
        "city": city,
        "locality": locality or None,
        "cuisines": cuisines,
        "avg_cost_for_two": cost,
        "rating": rating,
        "tags": [],
        "source_hash": _build_source_hash(name, city, locality, cuisines),
    }


def _ensure_schema(conn: Connection) -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    ddl = schema_path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()


def _insert_ingestion_run(conn: Connection, source_version: str) -> str:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO ingestion_runs (status, source_version)
            VALUES (%s, %s)
            RETURNING run_id::text
            """,
            ("running", source_version),
        )
        run_id = cur.fetchone()[0]
    conn.commit()
    return run_id


def _finalize_ingestion_run(
    conn: Connection,
    run_id: str,
    status: str,
    row_count: int,
    error_count: int,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE ingestion_runs
            SET status = %s,
                row_count = %s,
                error_count = %s,
                completed_at = NOW()
            WHERE run_id::text = %s
            """,
            (status, row_count, error_count, run_id),
        )
    conn.commit()


def _upsert_restaurants(conn: Connection, rows: list[dict[str, Any]]) -> int:
    inserted = 0
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                """
                INSERT INTO restaurants
                    (name, city, locality, cuisines, avg_cost_for_two, rating, tags, source_hash, updated_at)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (source_hash)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    locality = EXCLUDED.locality,
                    cuisines = EXCLUDED.cuisines,
                    avg_cost_for_two = EXCLUDED.avg_cost_for_two,
                    rating = EXCLUDED.rating,
                    tags = EXCLUDED.tags,
                    updated_at = NOW()
                """,
                (
                    row["name"],
                    row["city"],
                    row["locality"],
                    row["cuisines"],
                    row["avg_cost_for_two"],
                    row["rating"],
                    row["tags"],
                    row["source_hash"],
                ),
            )
            inserted += 1
    conn.commit()
    return inserted


def _snapshot_raw_records(raw_dir: Path, dataset_name: str, records: list[dict[str, Any]]) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = raw_dir / ts
    folder.mkdir(parents=True, exist_ok=True)
    snapshot_path = folder / "raw_snapshot.jsonl"
    with snapshot_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=True, default=str) + "\n")
    (folder / "meta.json").write_text(
        json.dumps({"dataset": dataset_name, "snapshot_ts": ts, "records": len(records)}, indent=2),
        encoding="utf-8",
    )
    return folder


def _write_quality_report(base_dir: Path, report: dict[str, Any]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = base_dir / f"quality_report_{ts}.json"
    csv_path = base_dir / f"quality_report_{ts}.csv"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for key, value in report.items():
            writer.writerow([key, value])


def run() -> None:
    settings = load_settings()
    raw_dir = Path(settings.raw_ingestion_dir)
    report_dir = Path("data_pipeline/reports")
    dataset = load_dataset(settings.hf_dataset_name)
    split_name = "train" if "train" in dataset else list(dataset.keys())[0]
    records = [dict(x) for x in dataset[split_name]]
    snapshot_folder = _snapshot_raw_records(raw_dir, settings.hf_dataset_name, records)

    normalized: list[dict[str, Any]] = []
    dropped = 0
    seen_hashes: set[str] = set()
    for rec in records:
        mapped = normalize_record(rec)
        if not mapped:
            dropped += 1
            continue
        if mapped["source_hash"] in seen_hashes:
            continue
        seen_hashes.add(mapped["source_hash"])
        normalized.append(mapped)

    source_version = f"{settings.hf_dataset_name}:{split_name}"

    with connect(settings.postgres_dsn) as conn:
        _ensure_schema(conn)
        run_id = _insert_ingestion_run(conn, source_version)
        try:
            upserted = _upsert_restaurants(conn, normalized)
            _finalize_ingestion_run(
                conn,
                run_id=run_id,
                status="success",
                row_count=upserted,
                error_count=dropped,
            )
        except Exception:
            _finalize_ingestion_run(
                conn,
                run_id=run_id,
                status="failed",
                row_count=0,
                error_count=len(records),
            )
            raise

    report = {
        "source_dataset": settings.hf_dataset_name,
        "source_split": split_name,
        "raw_records": len(records),
        "valid_records": len(normalized),
        "dropped_records": dropped,
        "deduplicated_records": len(records) - dropped - len(normalized),
        "snapshot_folder": str(snapshot_folder),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_quality_report(report_dir, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run()
