from src.clients.sqllite import SQLiteClient
import yfinance as yf
query = """
SELECT *
FROM raw_data
where current_date = '2025-02-22';
"""

db = "analysis_results.db"

client = SQLiteClient(db)

test = client.query(query)
ticker = yf.Ticker("^GSPC")
info = ticker.info
print(info)