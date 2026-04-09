from __future__ import annotations

from dotenv import load_dotenv
import os

from psycopg import connect


def main() -> None:
    load_dotenv()
    dsn = os.getenv("POSTGRES_DSN", "").strip()
    if not dsn:
        raise SystemExit("POSTGRES_DSN missing")

    with connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from restaurants")
            print("restaurants count:", cur.fetchone()[0])

            cur.execute("select count(distinct city) from restaurants")
            print("distinct cities:", cur.fetchone()[0])

            cur.execute(
                """
                select city, count(*) as c
                from restaurants
                group by city
                order by c desc
                limit 50
                """
            )
            rows = cur.fetchall()

    print("\nTop 50 city values by frequency:")
    for city, c in rows:
        print(f"{c:>6}  {city!r}")


if __name__ == "__main__":
    main()

