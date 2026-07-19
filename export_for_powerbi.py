import sqlite3
import pandas as pd
import os

conn = sqlite3.connect("nse_market_pulse.db")

tables = ["bhavcopy", "delivery", "bulk_deals", "fii_dii", "announcements"]

os.makedirs("powerbi_exports", exist_ok=True)

for table in tables:
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    df.to_csv(f"powerbi_exports/{table}.csv", index=False)
    print(f"{table}: exported {len(df)} rows")

conn.close()