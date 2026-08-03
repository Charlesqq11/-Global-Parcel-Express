import sqlite3

conn = sqlite3.connect("database/parcels.db")
cursor = conn.cursor()

cursor.execute("""
INSERT OR IGNORE INTO admins (username, password)
VALUES (?, ?)
""", ("admin", "@admin123@"))

conn.commit()
conn.close()

print("Admin account added successfully.")