import requests
import io
import zipfile
import pandas as pd
import sqlite3
import time
from datetime import date,timedelta

end_date = date.today()
start_date = end_date - timedelta(days=30)

print(start_date,end_date)

current_date = start_date
date_list = []

while current_date <= end_date:
    date_list.append(current_date)
    current_date += timedelta(days=1)

print(len(date_list))
print(date_list[:5])

trading_dates = [d for d in date_list if d.weekday()<5]

print(len(trading_dates))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

session= requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

all_days = []

for d in trading_dates:
    date_str = d.strftime("%Y%m%d")
    url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date_str}_F_0000.csv.zip"

    try:
        response = session.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"{date_str}: skipped (status {response.status_code})")
            continue

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        csv_filename = zip_file.namelist()[0]
        day_df = pd.read_csv(zip_file.open(csv_filename))

        all_days.append(day_df)
        print(f"{date_str}: OK ({len(day_df)} rows)")

    except Exception as e:
        print(f"{date_str}: failed - {e}")

    time.sleep(1)

print(f"\nTotal days successfully downloaded: {len(all_days)}")

combined_df = pd.concat(all_days, ignore_index=True)
print(combined_df.shape)

combined_df = combined_df.rename(columns={
    "TradDt": "trade_date",
    "TckrSymb": "symbol",
    "SctySrs": "series",
    "OpnPric": "open_price",
    "HghPric": "high_price",
    "LwPric": "low_price",
    "ClsPric": "close_price",
    "PrvsClsgPric": "prev_close_price",
    "TtlTradgVol": "volume",
    "TtlTrfVal": "turnover",
    "TtlNbOfTxsExctd": "num_trades",
})

combined_df = combined_df[combined_df["series"] == "EQ"]

combined_df = combined_df[["trade_date", "symbol", "series", "open_price", "high_price",
                            "low_price", "close_price", "prev_close_price", "volume",
                            "turnover", "num_trades"]]

print(combined_df.shape)
print(combined_df["trade_date"].nunique())

conn = sqlite3.connect("nse_market_pulse.db")

combined_df.to_sql("bhavcopy", conn, if_exists="replace", index=False)

conn.close()

print("Saved to database.")