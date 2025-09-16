from flask import Blueprint, render_template
from flask_login import login_required, current_user
import os
import sqlite3

farmer_advisory_bp = Blueprint("farmer_advisory", __name__, url_prefix="/farmer")

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

@farmer_advisory_bp.route("/dashboard-advisory")
@login_required
def dashboard():
    if current_user.role != "farmer":
        return "Unauthorized", 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Example: assuming `users` table has `district` and `crop` fields for farmers
    user_crop = getattr(current_user, "crop", None)
    user_district = getattr(current_user, "district", None)

    query = "SELECT id, title, message, crop, district, created_at FROM advisories ORDER BY created_at DESC"
    cursor.execute(query)
    advisories = cursor.fetchall()

    conn.close()

    # Filter advisories (show all if no crop/district set)
    filtered_advisories = []
    for adv in advisories:
        adv_dict = {
            "id": adv[0],
            "title": adv[1],
            "message": adv[2],
            "crop": adv[3],
            "district": adv[4],
            "created_at": adv[5]
        }

        if (not user_crop or not adv_dict["crop"] or adv_dict["crop"].lower() == user_crop.lower()) and \
           (not user_district or not adv_dict["district"] or adv_dict["district"].lower() == user_district.lower()):
            filtered_advisories.append(adv_dict)

    return render_template("farmer_dashboard.html", advisories=filtered_advisories)




@farmer_advisory_bp.route("/service")
@login_required
def services():
    if current_user.role != "farmer":
        return "Unauthorized", 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get farmer district (assumes `users` table has district column)
    user_district = getattr(current_user, "district", None)

    # Fetch services
    if user_district:
        cursor.execute("""
            SELECT id, name, service_type, district, contact, created_at
            FROM services
            WHERE district = ?
            ORDER BY created_at DESC
        """, (user_district,))
    else:
        cursor.execute("""
            SELECT id, name, service_type, district, contact, created_at
            FROM services
            ORDER BY created_at DESC
        """)

    services = cursor.fetchall()
    conn.close()

    # Convert into dicts for template
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

    return render_template("service_page.html", services=service_list)
