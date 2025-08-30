import sqlite3
from decimal import Decimal
from config import DB_PATH
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    #user's table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password TEXT NOT NULL,
            reset_token TEXT,
            profile_pic TEXT DEFAULT 'default,png',
            district TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('farmer', 'extension_worker', 'admin')) NOT NULL DEFAULT 'farmer',
            language TEXT CHECK(language IN ('en', 'ny')) NOT NULL DEFAULT 'en'
            )
        ''')

    #market_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        seller_name TEXT NOT NULL,
        contact_info TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    #forum_posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forum_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    #profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmer_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        farm_location TEXT,
        contact_info TEXT,
        crops TEXT,
        animals TEXT,
        bio TEXT,
        image_filename TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    #agrishare table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS share_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL UNIQUE,
        owner_user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        status TEXT DEFAULT 'active',
        FOREIGN KEY (owner_user_id) REFERENCES users(id)
        )
    ''')

    #agrishare table for shared files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        uploaded_by INTEGER NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES share_sessions(session_id),
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
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
        FOREIGN KEY(sender_id) REFERENCES users(id),
        FOREIGN KEY(receiver_id) REFERENCES users(id)
        )
    ''')

    #equipment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        model TEXT,
        condition TEXT,
        location TEXT,
        image_filename TEXT,
        owner_id INTEGER NOT NULL,
        FOREIGN KEY(owner_id) REFERENCES users(id)
        )
    ''')

    #equipment availability table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment_availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'unavailable',  -- could be 'unavailable' or 'available'
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
        )
    ''')

    #equipment booking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment_bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        FOREIGN KEY(equipment_id) REFERENCES equipment(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    #equipment log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment_maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        date DATE NOT NULL,
        cost REAL,
        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
        )
    ''')

    #event table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        location TEXT NOT NULL,
        date TEXT,
        time TEXT,
        organizer TEXT,
        flyer_path TEXT
        )
    ''')

    #notification tabel
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        link TEXT,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    #event registration table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(event_id) REFERENCES events(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    #knowledge hub table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT,
        file_url TEXT,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    #knowledge tagging table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id INTEGER,
        tag TEXT,
        FOREIGN KEY (resource_id) REFERENCES knowledge_resources(id) ON DELETE CASCADE
        )
    """)
    
    #famer management table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmer_management_profiles (
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        crop TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    #my fields and my   crop table
    #FIELD TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        size REAL NOT NULL,
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    #CROPS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        season TEXT,
        expected_yield REAL,
        planted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (field_id) REFERENCES fields (id)
        )
    ''')


    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
