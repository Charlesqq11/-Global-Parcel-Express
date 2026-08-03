import sqlite3

conn = sqlite3.connect("database/parcels.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Admins table created successfully.")