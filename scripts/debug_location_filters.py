from __future__ import annotations

import os

from dotenv import load_dotenv
from psycopg import connect


def main() -> None:
    load_dotenv()
    dsn = os.getenv("POSTGRES_DSN", "").strip()
    if not dsn:
        raise SystemExit("POSTGRES_DSN missing")

    location = os.getenv("DEBUG_LOCATION", "Whitefield")
    min_rating = float(os.getenv("DEBUG_MIN_RATING", "4.0"))
    low = float(os.getenv("DEBUG_LOW", "800"))
    high = float(os.getenv("DEBUG_HIGH", "2000"))
    pattern = f"%{location.lower()}%"

    with connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select count(*)
                from restaurants
                where lower(city) like %s or lower(coalesce(locality,'')) like %s
                """,
                (pattern, pattern),
            )
            print("location matches:", cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from restaurants
                where (lower(city) like %s or lower(coalesce(locality,'')) like %s)
                  and rating is not null
                """,
                (pattern, pattern),
            )
            print("location matches with rating present:", cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from restaurants
                where (lower(city) like %s or lower(coalesce(locality,'')) like %s)
                  and coalesce(rating,0) >= %s
                """,
                (pattern, pattern, min_rating),
            )
            print("location matches with min_rating:", cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from restaurants
                where (lower(city) like %s or lower(coalesce(locality,'')) like %s)
                  and (avg_cost_for_two is not null)
                """,
                (pattern, pattern),
            )
            print("location matches with cost present:", cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from restaurants
                where (lower(city) like %s or lower(coalesce(locality,'')) like %s)
                  and (avg_cost_for_two >= %s and avg_cost_for_two <= %s)
                """,
                (pattern, pattern, low, high),
            )
            print("location matches within budget band:", cur.fetchone()[0])

            cur.execute(
                """
                select count(*)
                from restaurants
                where (lower(city) like %s or lower(coalesce(locality,'')) like %s)
                  and coalesce(rating,0) >= %s
                  and (avg_cost_for_two >= %s and avg_cost_for_two <= %s)
                """,
                (pattern, pattern, min_rating, low, high),
            )
            print("location + min_rating + budget:", cur.fetchone()[0])


if __name__ == "__main__":
    main()

