import sqlite3

def create_tables():
    conn = sqlite3.connect("database/parcels.db")
    cursor = conn.cursor()

# Create the parcels table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_number TEXT UNIQUE NOT NULL,
        sender_name TEXT,
        receiver_name TEXT,
        status TEXT,
        location TEXT,
        updated_at TEXT
    )
    """)

    # Sample parcel records
    sample_parcels = [
        ("PKG1001", "John Smith", "Alice Brown", "In Transit", "New York", "2026-05-23 10:30:00"),
        ("PKG1002", "David Lee", "Emma Wilson", "Out for Delivery", "Los Angeles", "2026-05-23 11:15:00"),
        ("PKG1003", "Michael Johnson", "Sophia Davis", "Delivered", "Chicago", "2026-05-22 09:45:00")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO parcels
    (tracking_number, sender_name, receiver_name, status, location, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, sample_parcels)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Database created successfully")