import sqlite3

conn = sqlite3.connect("agriconnect.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO equipment (name, type, model, condition, location, image_filename, owner_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ("Tractor", "Machinery", "John Deere X350", "Good", "Farm A - East", "tractor.jpg", 1))

conn.commit()
conn.close()

print("Equipment added")

