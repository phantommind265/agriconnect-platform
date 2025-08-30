from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
import sqlite3
import os
from app.forms.message_form import MessageForm

message_bp = Blueprint("message_bp", __name__, url_prefix="/messages")

DB_PATH = os.path.join("app", "agriconnect.db")

# Inbox
@message_bp.route("/")
@login_required
def inbox():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.id, m.content, m.timestamp, u.username AS sender
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ?
        ORDER BY m.timestamp DESC
    """, (current_user.id,))
    messages = cursor.fetchall()
    conn.close()

    return render_template("messages/inbox.html", messages=messages)


@message_bp.route("/chat/<int:user_id>", methods=["GET", "POST"])
@login_required
def chat(user_id):
    form = MessageForm()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # get the other user's info
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    other_user = cursor.fetchone()
    if not other_user:
        flash("User not found", "danger")
        return redirect(url_for("message_bp.users_list"))

    if form.validate_on_submit():
        cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
                (current_user.id, other_user["id"], form.content.data)
                )
        conn.commit()
        return redirect(url_for("message_bp.chat", user_id=user_id))

    # fetch chat messages between current_user and other_user
    cursor.execute("""
        SELECT m.id, m.sender_id, m.receiver_id, m.content, m.timestamp, u.username AS sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE (m.sender_id = ? AND m.receiver_id = ?)
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.timestamp ASC
    """, (current_user.id, user_id, user_id, current_user.id))
    messages = cursor.fetchall()


    conn.close()
    return render_template("messages/chat.html", form=form, messages=messages, other_user=other_user)



@message_bp.route("/users")
@login_required
def users_list():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all users except the current one
    cursor.execute("SELECT id, username FROM users WHERE id != ?", (current_user.id,))
    users = cursor.fetchall()

    user_data = []
    for u in users:
        # fetch last message between current_user and this user
        cursor.execute("""
            SELECT content, timestamp, sender_id
            FROM messages
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY timestamp DESC LIMIT 1
        """, (current_user.id, u["id"], u["id"], current_user.id))
        last_msg = cursor.fetchone()

        if last_msg:
            preview = last_msg["content"][:30] + ("..." if len(last_msg["content"]) > 30 else "")
            sender = "You" if last_msg["sender_id"] == current_user.id else u["username"]
            timestamp = last_msg["timestamp"]
        else:
            preview = "No messages yet"
            sender = ""
            timestamp = ""

        user_data.append({
            "id": u["id"],
            "username": u["username"],
            "preview": f"{sender}: {preview}" if sender else preview,
            "timestamp": timestamp
        })

    conn.close()
    return render_template("messages/users_list.html", users=user_data)


