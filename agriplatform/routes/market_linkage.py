import sqlite3
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from agriplatform.forms.linkage_form import MarketLinkageForm
from agriplatform.forms.interest_form import ExpressInterestForm

linkage_bp = Blueprint("linkage", __name__, url_prefix="/linkage")
DB_PATH = os.path.join("agriplatform", "agriconnect.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@linkage_bp.teardown_app_request
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@linkage_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_market_linkage():
    if current_user.role not in ["admin", "extension_worker"]:
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    form = MarketLinkageForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute("""
            INSERT INTO market_linkages (crop, buyer_name, price_range, location, contact_info, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            form.crop.data,
            form.buyer_name.data,
            form.price_range.data,
            form.location.data,
            form.contact_info.data,
            form.notes.data,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        db.commit()
        flash("✅ Market linkage added successfully", "success")
        return redirect(url_for("linkage.add_market_linkage"))

    return render_template("add_market_linkage.html", form=form)


@linkage_bp.route("/view")
@login_required
def view_market():
    if current_user.role != "farmer":
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()

    # Fetch farmer's registered crops (assuming you have a crops table)
    farmer_crops = db.execute("SELECT crops FROM users WHERE id = ?",
                              (current_user.id,)).fetchall()
    crop_list = [c["crops"] for c in farmer_crops]

    # Fetch market linkages
    if crop_list:
        placeholders = ",".join("?" * len(crop_list))
        query = f"""
            SELECT * FROM market_linkages
            WHERE crop IN ({placeholders})
            ORDER BY created_at DESC
        """
        linkages = db.execute(query, crop_list).fetchall()
    else:
        # If no crops registered, show all linkages
        linkages = db.execute("SELECT * FROM market_linkages ORDER BY created_at DESC").fetchall()

    return render_template("view_market.html", linkages=linkages)


@linkage_bp.route("/express_interest/<int:market_id>", methods=["GET", "POST"])
@login_required
def express_interest(market_id):
    if current_user.role != "farmer":
        flash("Unauthorized access", "danger")
        return redirect(url_for("linkage.view_market"))

    db = get_db()
    market = db.execute("SELECT * FROM market_linkages WHERE id = ?", (market_id,)).fetchone()
    if not market:
        flash("Market opportunity not found", "danger")
        return redirect(url_for("linkage.view_market"))
    
    form = ExpressInterestForm()
    if form.validate_on_submit():
        message = form.message.data
        db.execute("""
            INSERT INTO market_interest (farmer_id, market_id, message, created_at)
            VALUES (?, ?, ?, ?)
        """, (current_user.id, market_id, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.commit()
        flash("✅ Interest expressed successfully!", "success")
        return redirect(url_for("linkage.view_market"))

    return render_template("express_interest.html", market=market, form=form)



@linkage_bp.route("/all_interests")
@login_required
def all_interests():
    if current_user.role not in ["admin", "extension_worker"]:
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    interests = db.execute("""
        SELECT mi.id, mi.message, mi.created_at,
               u.username AS farmer_name,
               m.buyer_name, m.crop
        FROM market_interest mi
        JOIN users u ON mi.farmer_id = u.id
        JOIN market_linkages m ON mi.market_id = m.id
        ORDER BY mi.created_at DESC
    """).fetchall()

    return render_template("all_market_interest.html", interests=interests)

