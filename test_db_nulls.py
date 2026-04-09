import os
from psycopg import connect
from dotenv import load_dotenv

load_dotenv()
dsn = os.getenv("POSTGRES_DSN")

with connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM restaurants WHERE rating IS NULL;")
        print("Rating NULL count:", cur.fetchone()[0])
        
        cur.execute("SELECT COUNT(*) FROM restaurants;")
        print("Total count:", cur.fetchone()[0])
        
        cur.execute("SELECT id, name, rating, avg_cost_for_two FROM restaurants LIMIT 5;")
        print("Sample:", cur.fetchall())
