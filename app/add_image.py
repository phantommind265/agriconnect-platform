import sqlite3

conn = sqlite3.connect("agriconnect.db")
cursor = conn.cursor()

cursor.execute('''
    ALTER TABLE market_items ADD COLUMN image_filename TEXT
''')

conn.commit()
conn.close()

print("image file path added")
