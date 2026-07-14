import requests
import pandas as pd
import sqlite3
import time
from datetime import date, timedelta, datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/report-detail/display-bulk-and-block-deals",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

# --- Holiday calendar (reused pattern) ---
holiday_url = "https://www.nseindia.com/api/holiday-master?type=trading"
holiday_response = session.get(holiday_url, headers=headers, timeout=10)
holiday_data = holiday_response.json()
holiday_dates_raw = [entry["tradingDate"] for entry in holiday_data["CM"]]
holiday_dates = [datetime.strptime(d, "%d-%b-%Y").date() for d in holiday_dates_raw]

# --- Date range ---
end_date = date.today()
start_date = end_date - timedelta(days=30)

current_date = start_date
date_list = []
while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

trading_dates = [d for d in date_list if d.weekday() < 5 and d not in holiday_dates]

print(f"Trading days to fetch: {len(trading_dates)}")

# --- Download loop: ONE request per day (this endpoint ignores date ranges) ---
all_days = []

for d in trading_dates:
    date_str = d.strftime("%d-%m-%Y")
    url = f"https://www.nseindia.com/api/historicalOR/bulk-block-short-deals?optionType=bulk_deals&from={date_str}&to={date_str}"

    try:
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"{date_str}: skipped (status {response.status_code})")
            continue

        day_data = response.json().get("data", [])

        if not day_data:
            print(f"{date_str}: no bulk deals recorded")
            continue

        day_df = pd.DataFrame(day_data)
        all_days.append(day_df)
        print(f"{date_str}: OK ({len(day_df)} rows)")

    except Exception as e:
        print(f"{date_str}: failed - {e}")

    time.sleep(1)

print(f"\nTotal days with data: {len(all_days)}")

# --- Combine and clean ---
combined_df = pd.concat(all_days, ignore_index=True)

combined_df["BD_DT_DATE"] = pd.to_datetime(combined_df["BD_DT_DATE"], format="%d-%b-%Y").dt.date

combined_df = combined_df.rename(columns={
    "BD_DT_DATE": "trade_date",
    "BD_SYMBOL": "symbol",
    "BD_SCRIP_NAME": "security_name",
    "BD_CLIENT_NAME": "client_name",
    "BD_BUY_SELL": "buy_sell",
    "BD_QTY_TRD": "qty_traded",
    "BD_TP_WATP": "avg_price",
})

combined_df = combined_df[["trade_date", "symbol", "security_name", "client_name",
                            "buy_sell", "qty_traded", "avg_price"]]

print(combined_df.shape)
print(combined_df.dtypes)

# --- Save to database ---
conn = sqlite3.connect("nse_market_pulse.db")
combined_df.to_sql("bulk_deals", conn, if_exists="replace", index=False)
conn.close()

print("Saved to database.")