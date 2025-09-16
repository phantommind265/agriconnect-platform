import sqlite3
import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from agriplatform.forms.notification_form import NotificationForm

notifications_bp = Blueprint("notifications", __name__)

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

def get_db():
    return sqlite3.connect(DB_PATH)

@notifications_bp.route("/send_notification", methods=["GET", "POST"])
@login_required
def send_notification():
    if current_user.role not in ["admin", "extension_worker"]:
        flash("Unauthorized", "danger")
        return redirect(url_for("auth.login"))

    form = NotificationForm()
    if form.validate_on_submit():
        db = get_db()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare recipients
        recipients = []
        if form.target.data == "all":
            recipients = [row[0] for row in db.execute("SELECT id FROM users").fetchall()]
        elif form.target.data in ["farmers", "extension", "admin"]:
            recipients = [row[0] for row in db.execute(
                "SELECT id FROM users WHERE role = ?", (form.target.data,)
            ).fetchall()]
        elif form.target.data == "user" and form.user_id.data.strip():
            recipients = [int(form.user_id.data.strip())]

        if not recipients:
            # If no specific recipients, insert as global notification (user_id NULL)
            db.execute("""
                INSERT INTO notifications (user_id, message, link, created_at)
                VALUES (?, ?, ?, ?)
            """, (None, form.message.data, form.link.data, created_at))
        else:
            for uid in recipients:
                db.execute("""
                    INSERT INTO notifications (user_id, message, link, created_at)
                    VALUES (?, ?, ?, ?)
                """, (uid, form.message.data, form.link.data, created_at))

        db.commit()
        db.close()
        flash("✅ Notification(s) sent successfully!", "success")
        return redirect(url_for("notifications.send_notification"))

    return render_template("send_notification.html", form=form)



@notifications_bp.route("/notifications")
@login_required
def all_notifications():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, message, link, created_at, is_read FROM notifications WHERE user_id = ? OR user_id IS NULL ORDER BY created_at DESC """,
                   (current_user.id,)).fetchall()
    # Mark all unread as read
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0",
                   (current_user.id,))
    conn.commit()
    conn.close()
    return render_template("all_notifications.html", notifications_bp=notifications_bp)


