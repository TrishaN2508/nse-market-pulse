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

conn.close()