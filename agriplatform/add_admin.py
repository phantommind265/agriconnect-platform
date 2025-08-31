import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("agriconnect.db")
cursor = conn.cursor()

username = "admin"
password = generate_password_hash("1234")
role = "admin"
lang = "en"

cursor.execute("INSERT INTO users (username, password, role, language) VALUES (?, ?, ?, ?)",
               (username, password, role, lang))

conn.commit()
conn.close()

print("Admin user created")

