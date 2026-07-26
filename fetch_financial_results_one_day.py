import requests
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-financial-results",
}

session = requests.Session()
session.get("https://www.nseindia.com", headers=headers, timeout=10)

url = "https://www.nseindia.com/api/corporates-financial-results?index=equities&period=Quarterly"

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)
print(response.text[:1000])

data = response.json()
df = pd.DataFrame(data)
print(df.shape)
print(df.columns.tolist())
print(df[["symbol", "companyName", "period", "xbrl"]].head(10))

print(df["xbrl"].value_counts().head(10))

xbrl_url = "https://nsearchives.nseindia.com/corporate/xbrl/INDAS_118503_1369510_03022025065013.xml"

xbrl_response = session.get(xbrl_url, headers=headers, timeout=10)
print(xbrl_response.status_code)
print(xbrl_response.text[:2000])

url = "https://www.nseindia.com/api/corporates-financial-results?index=equities&from_date=26-07-2025&to_date=26-07-2026&period=Quarterly"

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)

data = response.json()
df = pd.DataFrame(data)
print(df.shape)

url_test = "https://www.nseindia.com/api/corporates-financial-results?index=equities&from_date=01-07-2026&to_date=26-07-2026&period=Quarterly"

response_test = session.get(url_test, headers=headers, timeout=10)
data_test = response_test.json()
print(len(data_test))

url_year = "https://www.nseindia.com/api/corporates-financial-results?index=equities&from_date=26-07-2025&to_date=26-07-2026&period=Quarterly"

response_year = session.get(url_year, headers=headers, timeout=10)
data_year = response_year.json()
df_year = pd.DataFrame(data_year)

df_year["broadCastDate"] = pd.to_datetime(df_year["broadCastDate"], format="%d-%b-%Y %H:%M:%S")
df_year["month"] = df_year["broadCastDate"].dt.to_period("M")

print(df_year["month"].value_counts().sort_index())

url = "https://www.nseindia.com/api/integrated-filing-results?index=equities&from_date=26-06-2026&to_date=26-07-2026&period_ended=all&type=Integrated%20Filing-%20Financials&page=1&size=20"

response = session.get(url, headers=headers, timeout=10)
print(response.status_code)

data = response.json()
print(type(data))
if isinstance(data, dict):
    print(data.keys())

print(data["totalCount"])
print(data["size"], data["page"])
print(len(data["data"]))
print(data["data"][0])