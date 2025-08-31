import sqlite3

conn = sqlite3.connect("agriconnect.db")
cursor = conn.cursor()

sample_data = [
        ("Maize (50kg)", 25000, "High quality maize from Lilongwe", "Grains", "Hopeson Chikuse", "0997255736"),
        ("Groundnuts (10kg)", 15000, "Washed and sorted groundnuts", "Legumes", "Mary Chirwa", "088123456"),
        ("Fertizer (NPK)", 40000, "50kg NPK fertilizer for maize", "Inputs", "AgroTech Dealer", "098654321")
        ]

cursor.executemany('''
    INSERT INTO market_items (title, price, description, category, seller_name, contact_info)
    VALUES (?, ?, ?, ?, ?, ?)
''', sample_data)

conn.commit()
conn.close()

print("sample data added")

