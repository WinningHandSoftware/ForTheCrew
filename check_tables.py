import sqlite3

conn = sqlite3.connect('toke.db')
cursor = conn.cursor()

# Check tables in the database
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

conn.close()
