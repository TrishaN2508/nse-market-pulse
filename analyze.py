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

conn.close()