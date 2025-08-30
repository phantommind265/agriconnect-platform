from flask_login import UserMixin
import sqlite3
import os

DB_PATH = os.path.join("app", "agriconnect.db")

class User(UserMixin):
    def __init__(self, id, username, password, role, language):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.language = language

    def get_id(self):
        return str(self.id)

def get_user_by_username(username):
    """Fetch user by username(for login)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

def get_user_by_id(user_id):
    """Fetch user by ID(for session loading)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None
