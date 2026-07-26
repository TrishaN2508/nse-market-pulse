import requests
import pandas as pd
import sqlite3
from datetime import date, timedelta

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-integrated-filing",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

end_date = date.today()
start_date = end_date - timedelta(days=30)

from_str = start_date.strftime("%d-%m-%Y")
to_str = end_date.strftime("%d-%m-%Y")

# --- Probe for exact record count first ---
probe_url = (
    f"https://www.nseindia.com/api/integrated-filing-results?"
    f"index=equities&from_date={from_str}&to_date={to_str}"
    f"&period_ended=all&type=Integrated%20Filing-%20Financials"
    f"&page=0&size=1"
)
probe_response = session.get(probe_url, headers=headers, timeout=10)
total_count = probe_response.json()["totalCount"]
print(f"Total filings in range: {total_count}")

# --- Fetch exactly that many, plus a small buffer for filings arriving mid-request ---
actual_size = total_count + 50
url = (
    f"https://www.nseindia.com/api/integrated-filing-results?"
    f"index=equities&from_date={from_str}&to_date={to_str}"
    f"&period_ended=all&type=Integrated%20Filing-%20Financials"
    f"&page=0&size={actual_size}"
)
response = session.get(url, headers=headers, timeout=10)
data = response.json()

records = data["data"]
if len(records) != data["totalCount"]:
    print("WARNING: received count does not match reported total — investigate before trusting this data.")

df = pd.DataFrame(records)
df = df.drop_duplicates(subset="seq_Id")

df = df[["creation_Date", "symbol", "cmName", "qe_Date", "type_Sub",
         "consolidated", "audited"]]

df["creation_Date"] = pd.to_datetime(df["creation_Date"], format="%d-%b-%Y %H:%M:%S")
df["trade_date"] = df["creation_Date"].dt.date

df = df.rename(columns={
    "creation_Date": "filed_at",
    "cmName": "company_name",
    "qe_Date": "quarter_ended",
    "type_Sub": "filing_type",
})

df = df[["trade_date", "filed_at", "symbol", "company_name", "quarter_ended",
         "filing_type", "consolidated", "audited"]]

print(df.shape)

conn = sqlite3.connect("nse_market_pulse.db")
df.to_sql("financial_results_filings", conn, if_exists="replace", index=False)
conn.close()

print("Saved to database.")