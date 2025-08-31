import sqlite3
import os

DB_PATH = os.path.join("agriplatform", "agriconnect.db")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Suppose user 3 and 4 are farmers; user 2 is an extension worker
rows = [
    (3, "Lilongwe", "Area 25", "+265-999-000-001", "maize, soy", 2.0, 2),
    (4, "Mzuzu", "Chiputula", "+265-999-000-002", "tea, maize", 1.2, 2),
]
for r in rows:
    try:
        c.execute("""INSERT INTO farmer_profiles
                     (user_id, district, location, phone, crops, farm_size_acres, assigned_to)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", r)
    except:
        pass
conn.commit()
conn.close()
print("✅ Seeded sample farmer profiles.")

