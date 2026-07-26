import requests
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-shareholding-pattern",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = "https://www.nseindia.com/api/corporate-share-holdings-master?index=equities&from_date=26-06-2026&to_date=26-07-2026"

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)
print(response.text[:1000])

data = response.json()
df = pd.DataFrame(data)
print(df.shape)
print(df.columns.tolist())
print(df[["symbol", "name", "date", "pr_and_prgrp", "public_val", "employeeTrusts"]].head(10))

print(data if isinstance(data, dict) else "data is a plain list, not a dict")

print(type(data))
print(len(data))

print(df["date"].value_counts().sort_index())