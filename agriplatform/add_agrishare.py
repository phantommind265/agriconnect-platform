import sqlite3

def create_share_sessions_table():
    conn = sqlite3.connect('agriconnect.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS share_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL UNIQUE,
        owner_user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (owner_user_id) REFERENCES users(id)
    );
    ''')

    conn.commit()
    conn.close()

    print("agrishare table added")

if __name__ == "__main__":
    create_share_sessions_table()

