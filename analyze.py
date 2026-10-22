import sqlite3
import pandas as pd

conn = sqlite3.connect("nse_market_pulse.db")

# --- Top 10 stocks by volume ---
query1 = """
SELECT symbol, close_price, volume, turnover
FROM bhavcopy
ORDER BY volume DESC
LIMIT 10
"""
result1 = pd.read_sql(query1, conn)
print("Top 10 stocks by volume:")
print(result1)
print()

# --- Daily market-wide aggregates ---
query2 = """
SELECT trade_date, COUNT(DISTINCT symbol) AS num_stocks, SUM(volume) AS total_volume
FROM bhavcopy
GROUP BY trade_date
ORDER BY trade_date
"""
result2 = pd.read_sql(query2, conn)
print("Daily aggregates:")
print(result2)
print()

# --- Top 10 by volume, joined with delivery % ---
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
print("Top 10 by volume, with delivery %:")
print(result3)
print()

# --- Announcement category breakdown ---
query4 = """
SELECT category, COUNT(*) as cnt
FROM announcements
GROUP BY category
ORDER BY cnt DESC
"""
result4 = pd.read_sql(query4, conn)
print("Announcement categories:")
print(result4.to_string())
print()

conn.close()