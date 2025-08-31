import sqlite3

def init_db():
    conn = sqlite3.connect("agriconnect.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user',
            language TEXT CHECK(language IN ('en', 'ny')) NOT NULL DEFAULT 'en'
            )
        ''')

    #messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('sent', 'delivered', 'read')) DEFAULT 'sent',
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
            )
        ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
