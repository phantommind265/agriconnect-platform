from flask import Blueprint, render_template, flash, redirect, url_for
from agriplatform.forms.donation_form import DonationForm
import sqlite3
from datetime import datetime
import os

donation_bp = Blueprint("donation", __name__, url_prefix="/donations")
DB_PATH = os.path.join("agriplatform", "agriconnect.db")

@donation_bp.route("/", methods=["GET", "POST"])
def donations():
    form = DonationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        amount = float(form.amount.data)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO donations (name, email, amount, date) VALUES (?, ?, ?, ?)",
            (name, email, amount, datetime.now())
        )
        conn.commit()
        conn.close()

        flash("Thank you for your donation ❤️", "success")
        return redirect(url_for("donation.donations"))

    return render_template("donation.html", form=form)

