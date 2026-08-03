import sqlite3

conn = sqlite3.connect("database/parcels.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE parcels
ADD COLUMN receiver_email TEXT
""")

conn.commit()
conn.close()

print("Email column added successfully")