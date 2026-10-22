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

#end_date = date.today()
#start_date = end_date - timedelta(days=365)

conn = sqlite3.connect("nse_market_pulse.db")
last_date = pd.read_sql("SELECT MAX(trade_date) AS d FROM delivery", conn)["d"][0]
conn.close()

start_date = datetime.strptime(last_date, "%Y-%m-%d").date() + timedelta(days=1)
end_date = date.today()

current_date = start_date
date_list = []
while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

trading_dates = [d for d in date_list if d.weekday() < 5 and d not in holiday_dates]

print(f"Date range: {start_date} to {end_date}")
print(f"Trading days to fetch: {len(trading_dates)}")

all_days = []

for d in trading_dates:
    date_str = d.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"

    try:
        response = session.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"{date_str}: skipped (status {response.status_code})")
            continue

        day_df = pd.read_csv(io.StringIO(response.text))

        all_days.append(day_df)
        print(f"{date_str}: OK ({len(day_df)} rows)")

        if len(all_days) % 25 == 0:
            print(f"--- Progress: {len(all_days)} days downloaded so far ---")

    except Exception as e:
        print(f"{date_str}: failed - {e}")

    time.sleep(1)

print(f"\nTotal days successfully downloaded: {len(all_days)}")

if not all_days:
    print("Already up to date.")
    raise SystemExit

combined_df = pd.concat(all_days, ignore_index=True)

combined_df.columns = combined_df.columns.str.strip()

text_columns = combined_df.select_dtypes(include="object").columns
for col in text_columns:
    combined_df[col] = combined_df[col].str.strip()

combined_df = combined_df[combined_df["SERIES"] == "EQ"]

combined_df = combined_df[["DATE1", "SYMBOL", "SERIES", "DELIV_QTY", "DELIV_PER", "TTL_TRD_QNTY"]]

combined_df["DELIV_QTY"] = pd.to_numeric(combined_df["DELIV_QTY"], errors="coerce")
combined_df["DELIV_PER"] = pd.to_numeric(combined_df["DELIV_PER"], errors="coerce")
combined_df["DATE1"] = pd.to_datetime(combined_df["DATE1"], format="%d-%b-%Y").dt.date

combined_df = combined_df.rename(columns={
    "DATE1": "trade_date",
    "SYMBOL": "symbol",
    "SERIES": "series",
    "DELIV_QTY": "delivery_qty",
    "DELIV_PER": "delivery_pct",
    "TTL_TRD_QNTY": "traded_qty",
})
combined_df = combined_df[combined_df["trade_date"].astype(str) > last_date]
combined_df = combined_df.drop_duplicates(subset=["trade_date", "symbol"])

print(f"Clean dataset: {combined_df.shape}, {combined_df['trade_date'].nunique()} unique trading days")

conn = sqlite3.connect("nse_market_pulse.db")
combined_df.to_sql("delivery", conn, if_exists="append", index=False)
conn.close()

print("Saved to database.")