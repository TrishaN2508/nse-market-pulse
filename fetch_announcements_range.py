
import requests
import pandas as pd
import sqlite3
import time
from datetime import date, timedelta

# Date range: last 365 days
end_date = date.today()
start_date = end_date - timedelta(days=365)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()
session.headers.update(headers)

# Initialize the session and cookies
home = session.get("https://www.nseindia.com/", timeout=(10, 30))
print("NSE homepage status:", home.status_code)

all_data = []
batch_start = start_date

while batch_start <= end_date:
    batch_end = min(batch_start + timedelta(days=6), end_date)

    params = {
        "index": "equities",
        "from_date": batch_start.strftime("%d-%m-%Y"),
        "to_date": batch_end.strftime("%d-%m-%Y"),
        "reqXbrl": "false",
    }

    print(f"Fetching {params['from_date']} to {params['to_date']}")

    for attempt in range(3):
        try:
            response = session.get(
                "https://www.nseindia.com/api/corporate-announcements",
                params=params,
                timeout=(10, 60),
            )
            response.raise_for_status()
            batch_data = response.json()

            if not isinstance(batch_data, list):
                raise ValueError(
                    f"Unexpected API response: {str(batch_data)[:300]}"
                )

            all_data.extend(batch_data)
            print(f"  Retrieved {len(batch_data)} announcements")
            break

        except (requests.RequestException, ValueError) as e:
            print(f"  Attempt {attempt + 1} failed: {e}")

            if attempt == 2:
                raise RuntimeError(
                    f"Failed to fetch batch {params['from_date']} "
                    f"to {params['to_date']}"
                ) from e

            time.sleep(3 * (attempt + 1))

    batch_start = batch_end + timedelta(days=1)
    time.sleep(1.5)

# Convert to DataFrame
df = pd.DataFrame(all_data)

if df.empty:
    raise ValueError("No announcements were returned by NSE.")

print("Total records fetched:", len(df))
print("Available columns:", df.columns.tolist())

required = [
    "sort_date", "symbol", "sm_name",
    "desc", "attchmntText", "attchmntFile"
]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing expected columns: {missing}")

df = df[required].rename(columns={
    "sort_date": "announced_at",
    "sm_name": "company_name",
    "desc": "category",
    "attchmntText": "description",
    "attchmntFile": "attachment_url",
})

df["announced_at"] = pd.to_datetime(
    df["announced_at"], errors="coerce"
)

df = df.dropna(subset=["announced_at"])
df["trade_date"] = df["announced_at"].dt.date

df = df[[
    "trade_date",
    "announced_at",
    "symbol",
    "company_name",
    "category",
    "description",
    "attachment_url",
]]

# Remove duplicates in case the API returns overlapping records
df = df.drop_duplicates()

# Save to SQLite
with sqlite3.connect("nse_market_pulse.db") as conn:
    df.to_sql(
        "announcements",
        conn,
        if_exists="replace",
        index=False
    )

print("Saved successfully!")
print("Final shape:", df.shape)
print(df.head())
