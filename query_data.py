from src.clients.sqllite import SQLiteClient
query = """
SELECT *
FROM data
"""

db = "main.db"

client = SQLiteClient(db)

test = client.query(query)

print(test)