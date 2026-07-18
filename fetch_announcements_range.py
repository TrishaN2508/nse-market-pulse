import requests
import pandas as pd
from datetime import date, timedelta

end_date = date.today()
start_date = end_date - timedelta(days=30)

from_str = start_date.strftime("%d-%m-%Y")
to_str = end_date.strftime("%d-%m-%Y")


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = f"https://www.nseindia.com/api/corporate-announcements?index=equities&from_date={from_str}&to_date={to_str}&reqXbrl=false"

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)

data = response.json()
df = pd.DataFrame(data)
print(df.shape)
print(df["an_dt"].str[:10].unique())

print(df.columns.tolist())
print(df.dtypes)

df = df[["sort_date", "symbol", "sm_name", "desc", "attchmntText", "attchmntFile"]]

df = df.rename(columns={
    "sort_date": "announced_at",
    "symbol": "symbol",
    "sm_name": "company_name",
    "desc": "category",
    "attchmntText": "description",
    "attchmntFile": "attachment_url",
})

print(df.shape)
print(df.head())

df["announced_at"] = pd.to_datetime(df["announced_at"])
df["trade_date"] = df["announced_at"].dt.date

df = df[["trade_date", "announced_at", "symbol", "company_name", "category", "description", "attachment_url"]]

print(df.dtypes)

import sqlite3
conn = sqlite3.connect("nse_market_pulse.db")
df.to_sql("announcements", conn, if_exists="replace", index=False)
conn.close()

print("Saved to database.")