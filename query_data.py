from src.clients.sqllite import SQLiteClient
query = """
SELECT *
FROM raw_data
"""

db = "analysis_results.db"

client = SQLiteClient(db)

test = client.query(query)

print(test)