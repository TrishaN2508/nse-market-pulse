import requests
import io
import pandas as pd

DATE_STR = "10072026"  # format: DDMMYYYY — different from bhavcopy's YYYYMMDD!

url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{DATE_STR}.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)

df = pd.read_csv(io.StringIO(response.text))
print(df.shape)
print(df.columns.tolist())

df.columns = df.columns.str.strip()
print(df.columns.tolist())

print(df["SERIES"].unique())
df["SERIES"] = df["SERIES"].str.strip()
print(df["SERIES"].unique())

print(df[["SYMBOL", "SERIES", "DELIV_QTY", "DELIV_PER"]].head(10))
print(df["DELIV_PER"].describe())

df["DELIV_PER"] = pd.to_numeric(df["DELIV_PER"], errors="coerce")
print(df["DELIV_PER"].describe())
print(df["DELIV_PER"].isna().sum())

df = df[df["SERIES"] == "EQ"]

df = df[["DATE1", "SYMBOL", "SERIES", "DELIV_QTY", "DELIV_PER", "TTL_TRD_QNTY"]]

print(df.shape)
print(df.head())

print(df["SERIES"].unique())

text_columns = df.select_dtypes(include="object").columns
print(text_columns.tolist())

for col in text_columns:
    df[col] = df[col].str.strip()

df["DELIV_QTY"] = pd.to_numeric(df["DELIV_QTY"], errors="coerce")

df["DATE1"] = pd.to_datetime(df["DATE1"], format="%d-%b-%Y").dt.date

df = df.rename(columns={
    "DATE1": "trade_date",
    "SYMBOL": "symbol",
    "SERIES": "series",
    "DELIV_QTY": "delivery_qty",
    "DELIV_PER": "delivery_pct",
    "TTL_TRD_QNTY": "traded_qty",
})

print(df.dtypes)
print(df.head())