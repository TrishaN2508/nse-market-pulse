import requests
import pandas as pd
import os
from pathlib import Path

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

df["date"] = pd.to_datetime(df["date"], format="%d-%b-%Y").dt.date
df["buyValue"] = pd.to_numeric(df["buyValue"], errors="coerce")
df["sellValue"] = pd.to_numeric(df["sellValue"], errors="coerce")
df["netValue"] = pd.to_numeric(df["netValue"], errors="coerce")

df = df.rename(columns={
    "date": "trade_date",
    "buyValue": "buy_value_cr",
    "sellValue": "sell_value_cr",
    "netValue": "net_value_cr",
})

df = df[["trade_date", "category", "buy_value_cr", "sell_value_cr", "net_value_cr"]]

# --- CSV-based storage (works without a local database) ---
Path("data").mkdir(exist_ok=True)
csv_path = "data/fii_dii_history.csv"

today_str = str(df["trade_date"].iloc[0])

if os.path.exists(csv_path):
    existing = pd.read_csv(csv_path)
    existing["trade_date"] = existing["trade_date"].astype(str)

    if today_str in existing["trade_date"].values:
        existing = existing[existing["trade_date"] != today_str]
        print(f"Cleared existing rows for {today_str} (will re-add fresh data).")

    combined = pd.concat([existing, df.astype({"trade_date": str})], ignore_index=True)
else:
    combined = df.astype({"trade_date": str})
    print("Creating new history file.")

combined = combined.sort_values("trade_date").reset_index(drop=True)
combined.to_csv(csv_path, index=False)

print(f"Saved {len(df)} rows for {today_str}. Total history: {len(combined)} rows.")