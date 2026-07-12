import requests
import io
import pandas as pd
import sqlite3
import time
from datetime import date, timedelta, datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

holiday_url = "https://www.nseindia.com/api/holiday-master?type=trading"
holiday_response = session.get(holiday_url, headers=headers, timeout=10)

holiday_data = holiday_response.json()
holiday_dates_raw = [entry["tradingDate"] for entry in holiday_data["CM"]]
holiday_dates = [datetime.strptime(d, "%d-%b-%Y").date() for d in holiday_dates_raw]

# --- Build the date range to fetch ---
end_date = date.today()
start_date = end_date - timedelta(days=30)

current_date = start_date
date_list = []
while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

# Keep weekdays only, excluding known NSE holidays
trading_dates = [d for d in date_list if d.weekday() < 5 and d not in holiday_dates]

print(f"Date range: {start_date} to {end_date}")
print(f"Trading days to fetch: {len(trading_dates)}")

# --- Download loop ---
all_days = []

for d in trading_dates:
    date_str = d.strftime("%Y%m%d")
    