import sqlite3
import pandas as pd

conn = sqlite3.connect("nse_market_pulse.db")

query = """
SELECT symbol, close_price, volume, turnover
FROM bhavcopy
ORDER BY volume DESC
LIMIT 10
"""

result = pd.read_sql(query, conn)
print(result)



query2 = """
SELECT trade_date, COUNT(DISTINCT symbol) AS num_stocks, SUM(volume) AS total_volume
FROM bhavcopy
GROUP BY trade_date
ORDER BY trade_date
"""

result2 = pd.read_sql(query2, conn)
print(result2)

query3 = """
SELECT b.trade_date, b.symbol, b.volume, b.close_price,
       d.delivery_pct, d.delivery_qty
FROM bhavcopy b
JOIN delivery d
    ON b.trade_date = d.trade_date
    AND b.symbol = d.symbol
ORDER BY b.volume DESC
LIMIT 10
"""

result3 = pd.read_sql(query3, conn)
print(result3)

conn.close()

conn = sqlite3.connect("nse_market_pulse.db")
categories = pd.read_sql("SELECT category, COUNT(*) as cnt FROM announcements GROUP BY category ORDER BY cnt DESC", conn)
conn.close()
print(categories.to_string())

conn = sqlite3.connect("nse_market_pulse.db")
check = pd.read_sql("SELECT * FROM fii_dii ORDER BY trade_date DESC LIMIT 4", conn)
conn.close()
print(check)


conn = sqlite3.connect("nse_market_pulse.db")
dup_check = pd.read_sql("""
    SELECT trade_date, COUNT(*) as row_count
    FROM delivery
    GROUP BY trade_date
    HAVING COUNT(*) > 3000
    ORDER BY row_count DESC
""", conn)
conn.close()
print(dup_check)

conn = sqlite3.connect("nse_market_pulse.db")
dup_check = pd.read_sql("""
    SELECT trade_date, COUNT(*) as row_count
    FROM bhavcopy
    GROUP BY trade_date
    HAVING COUNT(*) > 3000
    ORDER BY row_count DESC
""", conn)
conn.close()
print(dup_check)
print(f"Total duplicate-flagged dates: {len(dup_check)}")

conn = sqlite3.connect("nse_market_pulse.db")
df = pd.read_sql("SELECT * FROM bulk_deals", conn)
conn.close()

print(f"Total rows: {len(df)}")
print(f"Fully duplicate rows (all columns identical): {df.duplicated().sum()}")

