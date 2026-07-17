import requests
import pandas as pd
import sqlite3

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/reports/fii-dii",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = "https://www.nseindia.com/api/fiidiiTradeReact"
response = session.get(url, headers=headers, timeout=10)

print(response.status_code)

data = response.json()
df = pd.DataFrame(data)
print(df)

df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y").dt.date
df["buyValue"] = pd.to_numeric(df["buyValue"], errors="coerce")
df["sellValue"] = pd.to_numeric(df["sellValue"], errors="coerce")
df["netValue"] = pd.to_numeric(df["netValue"], errors="coerce")

df = df.rename(columns={
    "date": "trade_date",
    "category": "category",
    "buyValue": "buy_value_cr",
    "sellValue": "sell_value_cr",
    "netValue": "net_value_cr",
})

df = df[["trade_date", "category", "buy_value_cr", "sell_value_cr", "net_value_cr"]]

print(df.dtypes)
print(df)

conn = sqlite3.connect("nse_market_pulse.db")
cursor = conn.cursor()

today_str = str(df["trade_date"].iloc[0])

table_exists = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='fii_dii'",
    conn
)

if len(table_exists) > 0:
    cursor.execute("DELETE FROM fii_dii WHERE trade_date = ?", (today_str,))
    conn.commit()
    print(f"Cleared any existing rows for {today_str} (if present).")

df.to_sql("fii_dii", conn, if_exists="append", index=False)
print(f"Saved {len(df)} rows for {today_str}.")

conn.close()
