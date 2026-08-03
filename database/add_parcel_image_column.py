import sqlite3

conn = sqlite3.connect("database/parcels.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE parcels
ADD COLUMN parcel_image TEXT
""")

conn.commit()
conn.close()

print("parcel_image column added successfully!")