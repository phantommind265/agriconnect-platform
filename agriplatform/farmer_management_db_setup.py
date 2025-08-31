import sqlite3
import os

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

def add_column_if_missing(cursor, table, column, coltype):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Base table
c.execute("""
CREATE TABLE IF NOT EXISTS farmer_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    district TEXT,
    location TEXT,
    phone TEXT,
    crops TEXT,              -- comma-separated list
    farm_size_acres REAL,
    assigned_to INTEGER,     -- extension worker user_id
    last_visit DATE,
    notes TEXT,
    photo TEXT,              -- path in /static/uploads
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
)
""")

# If the table existed already, ensure columns exist
for col, coltype in [
    ("district","TEXT"),
    ("location","TEXT"),
    ("phone","TEXT"),
    ("crops","TEXT"),
    ("farm_size_acres","REAL"),
    ("assigned_to","INTEGER"),
    ("last_visit","DATE"),
    ("notes","TEXT"),
    ("photo","TEXT"),
    ("created_at","TIMESTAMP"),
    ("updated_at","TIMESTAMP"),
]:
    add_column_if_missing(c, "farmer_profiles", col, coltype)

# Helpful indexes
c.execute("CREATE INDEX IF NOT EXISTS idx_farmer_profiles_user ON farmer_profiles(user_id)")
c.execute("CREATE INDEX IF NOT EXISTS idx_farmer_profiles_assigned ON farmer_profiles(assigned_to)")
c.execute("CREATE INDEX IF NOT EXISTS idx_farmer_profiles_district ON farmer_profiles(district)")

conn.commit()
conn.close()
print("✅ farmer_profiles table ready.")

