import sqlite3
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from agriplatform.forms.advisory_form import AdvisoryForm

advisory_bp = Blueprint("advisory", __name__, url_prefix="/advisory")

DB_PATH = os.path.join("agriplatform",  "agriconnect.db")

@advisory_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_advisory():
    # Only allow admin or extension worker
    if current_user.role not in ["admin", "extension_worker"]:
        flash("You are not authorized to post advisories.", "danger")
        return redirect(url_for("home.html"))

    form = AdvisoryForm()
    if form.validate_on_submit():
        title = form.title.data
        message = form.message.data
        crop = form.crop.data or None
        district = form.district.data or None
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO advisories (title, message, crop, district, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title, message, crop, district, created_at))
        conn.commit()
        conn.close()

        flash("Advisory posted successfully!", "success")
        return redirect(url_for("advisory.new_advisory"))

    return render_template("new_advisory.html", form=form)




