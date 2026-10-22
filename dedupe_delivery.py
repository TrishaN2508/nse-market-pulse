import sqlite3
import pandas as pd

conn = sqlite3.connect("nse_market_pulse.db")
df = pd.read_sql("SELECT * FROM delivery", conn)

print(f"Before dedup: {df.shape}")

df = df.drop_duplicates(subset=["trade_date", "symbol"])

print(f"After dedup: {df.shape}")

df.to_sql("delivery", conn, if_exists="replace", index=False)
conn.close()

print("Deduplicated and saved.")