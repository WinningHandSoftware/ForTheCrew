import sqlite3

# Connect to the database
conn = sqlite3.connect('toke.db')
cursor = conn.cursor()

# Delete the specific entry for Wednesday 22
cursor.execute("DELETE FROM Toke WHERE date = '2023-11-22'")
conn.commit()

# Verify deletion
cursor.execute("SELECT * FROM Toke WHERE date = '2023-11-22'")
print("Remaining Entries:", cursor.fetchall())

# Close the connection
conn.close()
