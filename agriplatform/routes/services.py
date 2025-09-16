import sqlite3
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from agriplatform.forms.service_form import ServiceForm
import os

services_bp = Blueprint("services", __name__, url_prefix="/services")

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

@services_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_service():
    # Only allow admin or extension worker
    if current_user.role not in ["admin", "extension_worker"]:
        flash("You are not authorized to add services.", "danger")
        return redirect(url_for("farmer.dashboard"))

    form = ServiceForm()
    if form.validate_on_submit():
        name = form.name.data
        service_type = form.service_type.data
        district = form.district.data
        contact = form.contact.data or None
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO services (name, service_type, district, contact, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, service_type, district, contact, created_at))
        conn.commit()
        conn.close()

        flash("Service added successfully!", "success")
        return redirect(url_for("services.new_service"))

    return render_template("new_service.html", form=form)



@services_bp.route("/all", methods=["GET", "POST"])
@login_required
def all_services():
    if current_user.role != "farmer":
        return "Unauthorized", 403

    search = request.args.get("search", "").strip().lower()
    filter_type = request.args.get("type", "")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT id, name, service_type, district, contact, created_at FROM services"
    params = []

    # Apply filters dynamically
    conditions = []
    if search:
        conditions.append("(LOWER(name) LIKE ? OR LOWER(service_type) LIKE ? OR LOWER(district) LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    if filter_type:
        conditions.append("service_type = ?")
        params.append(filter_type)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, tuple(params))
    services = cursor.fetchall()
    conn.close()

    service_list = [
        {
            "id": s[0],
            "name": s[1],
            "service_type": s[2],
            "district": s[3],
            "contact": s[4],
            "created_at": s[5]
        }
        for s in services
    ]

    return render_template("all_services.html", services=service_list, search=search, filter_type=filter_type)


@services_bp.route("/seed", methods=["GET"])
def seed_services():
    services_data = [
        ("Green Agro Shop", "Agro-dealer", "Lilongwe", "0991234567"),
        ("Sunrise Vet Clinic", "Veterinary", "Mzuzu", "0887654321"),
        ("Chisomo Market", "Market", "Blantyre", "0971112223"),
        ("Agri Input Dealers Ltd", "Agro-dealer", "Lilongwe", "0998889990"),
        ("Farm Care Vet Center", "Veterinary", "Zomba", "0881239876"),
        ("Mzimba Farmers Market", "Market", "Mzimba", "0972223334"),
        ("Extension Officer Banda", "Extension Officer", "Kasungu", "0995556667"),
        ("Better Harvest Agro", "Agro-dealer", "Dedza", "0884445556"),
        ("Community Vet Services", "Veterinary", "Mangochi", "0992221110"),
        ("Ntcheu Central Market", "Market", "Ntcheu", "0977778889")
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    from datetime import datetime
    for name, stype, district, contact in services_data:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO services (name, service_type, district, contact, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, stype, district, contact, created_at))
    conn.commit()
    conn.close()
    return "✅ 10 startup services added successfully."

