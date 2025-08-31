from flask import Blueprint, jsonify, session
import sqlite3
import os

notifications_bp = Blueprint('notifications', __name__)
DB_PATH = os.path.join("agriplatform", "agriconnect.db")

def get_unread_notifications(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, message, link, created_at
        FROM notifications
        WHERE user_id = ? AND is_read = 0
        ORDER BY created_at DESC
    """, (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

@notifications_bp.route("/notifications", methods=["GET"])
def notifications():
    # Check if user is logged in
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    notifications = get_unread_notifications(user_id)

    # Convert to JSON-friendly list
    notifications_list = []
    for notif in notifications:
        notifications_list.append({
            "id": notif[0],
            "message": notif[1],
            "link": notif[2],
            "created_at": notif[3]
        })

    return jsonify({"notifications": notifications_list})
