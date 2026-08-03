import sqlite3

conn = sqlite3.connect("database/parcels.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS parcel_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parcel_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    location TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parcel_id) REFERENCES parcels(id)
)
""")

conn.commit()
conn.close()

print("Parcel history table created successfully!")