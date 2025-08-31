from flask_login import UserMixin
import sqlite3
import os

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

class User(UserMixin):
    def __init__(self, id, username, role, language, password_hash, profile_pic="default.png"):
        self.id = id
        self.username = username
        self.role = role
        self.language = language
        self.password_hash = password_hash
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, language, password FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], username=row[1], role=row[2], language=row[3], password_hash=row[4])
        return None

    @staticmethod
    def find_by_username(username):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, language, password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], username=row[1], role=row[2], language=row[3], password_hash=row[4])
        return None

