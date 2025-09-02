import os
from config import DB_PATH
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import sqlite3
from agriplatform.forms.edit_profile_form import EditProfileForm

profile_bp = Blueprint("profile_bp", __name__)

UPLOAD_FOLDER = os.path.join("agriplatform", "static", "uploads" "profile_pic")

@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        file = form.profile_pic.data
        filename = current_user.profile_pic or "default.png"

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

        # update DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (filename, current_user.id))
        conn.commit()
        conn.close()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile_bp.view_profile"))

    return render_template("profile/edit_profile.html", form=form)

@profile_bp.route("/profile")
@login_required
def view_profile():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
    user = cursor.fetchone()
    conn.close()
    return render_template("profile/view_profile.html", user=user)

