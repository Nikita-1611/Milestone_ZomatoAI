import os
from psycopg import connect
from dotenv import load_dotenv

load_dotenv()
dsn = os.getenv("POSTGRES_DSN")

with connect(dsn) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT city FROM restaurants LIMIT 10;")
        print("CITIES:", cur.fetchall())
        
        cur.execute("SELECT DISTINCT locality FROM restaurants LIMIT 10;")
        print("LOCALITIES:", cur.fetchall())
