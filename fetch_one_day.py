import requests
import io
import zipfile
import pandas as pd
import sqlite3

DATE_STR="20260710"
url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{DATE_STR}_F_0000.csv.zip"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

session = requests.Session()

session.get("https://www.nseindia.com", headers=headers, timeout=10)

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)

zip_file = zipfile.ZipFile(io.BytesIO(response.content))
print(zip_file.namelist())

csv_filename = zip_file.namelist()[0]
df = pd.read_csv(zip_file.open(csv_filename))
print(df.shape)
print(df.head())

print(df.columns.tolist())

df = df.rename(columns={
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

df = df[["trade_date", "symbol", "series", "open_price", "high_price",
         "low_price", "close_price", "prev_close_price", "volume",
         "turnover", "num_trades"]]

print(df.head())

print(df["series"].unique())

df = df[df["series"] == "EQ"]
print(df.shape)
print(df["series"].unique())

conn = sqlite3.connect("nse_market_pulse.db")

df.to_sql("bhavcopy", conn, if_exists="replace", index=False)

conn.close()

print("Saved to database.")