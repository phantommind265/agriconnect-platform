import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
#from app.utils.roles import require_role
from config import DB_PATH
from datetime import datetime

ext_bp = Blueprint("ext", __name__, template_folder="../templates")

def db():
    return sqlite3.connect(DB_PATH)

# ---- Helpers ----
def query_farmers(assigned_to, q=None, district=None, crop=None):
    conn = db()
    cur = conn.cursor()
    sql = """
    SELECT fp.id, u.id as user_id, u.username, fp.district, fp.location, fp.phone, fp.crops,
           fp.farm_size_acres, fp.last_visit, fp.notes
    FROM farmer_profiles fp
    JOIN users u ON u.id = fp.user_id
    WHERE (fp.assigned_to = ? OR ? IS NULL)
    """
    params = [assigned_to, assigned_to]  # if admin, assigned_to may be None
    if q:
        sql += " AND (u.username LIKE ? OR fp.phone LIKE ? OR fp.location LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like, like])
    if district:
        sql += " AND fp.district = ?"
        params.append(district)
    if crop:
        sql += " AND (fp.crops LIKE ?)"
        params.append(f"%{crop}%")
    sql += " ORDER BY u.username ASC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_farmer_profile(fp_id):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT fp.id, u.id, u.username, fp.district, fp.location, fp.phone, fp.crops,
               fp.farm_size_acres, fp.assigned_to, fp.last_visit, fp.notes, fp.photo
        FROM farmer_profiles fp
        JOIN users u ON u.id = fp.user_id
        WHERE fp.id = ?
    """, (fp_id,))
    row = cur.fetchone()
    conn.close()
    return row

def get_extension_workers():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role IN ('extension','extension_worker')")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_farmers_without_profile():
    # helpful for creating profiles for existing farmer users
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username
        FROM users u
        WHERE u.role = 'farmer' AND u.id NOT IN (SELECT user_id FROM farmer_profiles)
        ORDER BY u.username
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

# ---- Routes ----

@ext_bp.route("/ext/farmers")
#@require_role("extension", "extension_worker", "admin")
def farmers_list():
    user_role = session.get("role")
    user_id = session.get("user_id")
    # Admins can see all; extension workers see only their assigned farmers
    assigned_filter = None if user_role == "admin" else user_id

    q = request.args.get("q") or None
    district = request.args.get("district") or None
    crop = request.args.get("crop") or None

    farmers = query_farmers(assigned_filter, q, district, crop)
    districts = sorted({f[3] for f in farmers if f[3]})  # from results
    return render_template("ext/farmers_list.html",
                           farmers=farmers, q=q, district=district, crop=crop, districts=districts)

@ext_bp.route("/ext/farmers/<int:fp_id>", methods=["GET", "POST"])
#@require_role("extension", "extension_worker", "admin")
def farmer_detail(fp_id):
    row = get_farmer_profile(fp_id)
    if not row:
        abort(404)

    # Restrict extension workers to their assigned farmers
    role = session.get("role")
    user_id = session.get("user_id")
    assigned_to = row[8]  # assigned_to
    if role in ("extension", "extension_worker") and assigned_to not in (None, user_id):
        abort(403)

    if request.method == "POST":
        district = request.form.get("district") or None
        location = request.form.get("location") or None
        phone = request.form.get("phone") or None
        crops = request.form.get("crops") or None
        farm_size_acres = request.form.get("farm_size_acres") or None
        last_visit = request.form.get("last_visit") or None
        notes = request.form.get("notes") or None
        reassign_to = request.form.get("assigned_to") or None
        if reassign_to == "": reassign_to = None

        conn = db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE farmer_management_profiles
            SET district = ?, location = ?, phone = ?, crops = ?, farm_size_acres = ?,
                assigned_to = ?, last_visit = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """, (district, location, phone, crops, farm_size_acres, reassign_to, last_visit, notes, datetime.now(), fp_id))
        conn.commit()
        conn.close()
        flash("Farmer profile updated.", "success")
        return redirect(url_for("ext.farmer_detail", fp_id=fp_id))

    extensions = get_extension_workers()
    return render_template("ext/farmer_detail.html", row=row, extensions=extensions)

@ext_bp.route("/ext/farmers/new", methods=["GET","POST"])
#@require_role("extension", "extension_worker", "admin")
def farmer_new():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        district = request.form.get("district") or None
        location = request.form.get("location") or None
        phone = request.form.get("phone") or None
        crops = request.form.get("crops") or None
        farm_size_acres = request.form.get("farm_size_acres") or None
        assigned_to = request.form.get("assigned_to") or session.get("user_id")

        conn = db()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO farmer_management_profiles (user_id, district, location, phone, crops, farm_size_acres, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, district, location, phone, crops, farm_size_acres, assigned_to))
            conn.commit()
            flash("Farmer profile created.", "success")
            return redirect(url_for("ext.farmers_list"))
        except sqlite3.IntegrityError as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()

    farmer_users = get_farmers_without_profile()
    extensions = get_extension_workers()
    return render_template("ext/farmer_new.html", farmer_users=farmer_users, extensions=extensions)
