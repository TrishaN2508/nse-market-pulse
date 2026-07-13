import sqlite3
import pandas as pd
from scipy import stats

conn = sqlite3.connect("nse_market_pulse.db")

query = """
SELECT b.trade_date, b.symbol, b.volume, d.delivery_pct
FROM bhavcopy b
JOIN delivery d
    ON b.trade_date = d.trade_date
    AND b.symbol = d.symbol
WHERE d.delivery_pct IS NOT NULL
"""

df = pd.read_sql(query, conn)
conn.close()

print(df.shape)
print(df.head())

threshold = df["volume"].quantile(0.90)
print(f"90th percentile volume threshold: {threshold:,.0f}")

high_volume = df[df["volume"] >= threshold]
normal_volume = df[df["volume"] < threshold]

print(f"High volume group: {len(high_volume)} rows")
print(f"Normal volume group: {len(normal_volume)} rows")

high_vol_mean = high_volume["delivery_pct"].mean()
normal_vol_mean = normal_volume["delivery_pct"].mean()

print(f"High volume group - avg delivery %: {high_vol_mean:.2f}")
print(f"Normal volume group - avg delivery %: {normal_vol_mean:.2f}")
print(f"Difference: {normal_vol_mean - high_vol_mean:.2f} percentage points")

t_stat, p_value = stats.ttest_ind(
    high_volume["delivery_pct"],
    normal_volume["delivery_pct"],
    equal_var=False
)

print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.10f}")