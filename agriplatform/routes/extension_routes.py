from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3
import os
from agriplatform.forms.extension_form import FarmerSearchForm

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

extension_bp = Blueprint('extension', __name__, template_folder='templates/extension')

def is_extension():
    return current_user.role == 'extension_worker'

@extension_bp.route('/farmers', methods=['GET', 'POST'])
@login_required
def manage_farmers():
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    form = FarmerSearchForm()
    query = "SELECT id, username, email, district, status, crop FROM users WHERE role='farmer'"
    params = []

    if form.validate_on_submit():
        if form.username.data:
            query += " AND username LIKE ?"
            params.append(f"%{form.username.data}%")
        if form.district.data:
            query += " AND district LIKE ?"
            params.append(f"%{form.district.data}%")
        if form.status.data:
            query += " AND status = ?"
            params.append(form.status.data)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    farmers = cursor.fetchall()
    conn.close()

    return render_template('farmer_management/extension_farmers.html', form=form, farmers=farmers)

@extension_bp.route('/farmers/toggle_status/<int:farmer_id>')
@login_required
def toggle_farmer_status(farmer_id):
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE id=? AND role='farmer'", (farmer_id,))
    result = cursor.fetchone()
    if result:
        new_status = 'inactive' if result[0] == 'active' else 'active'
        cursor.execute("UPDATE users SET status=? WHERE id=?", (new_status, farmer_id))
        conn.commit()
        flash(f"Farmer status updated to {new_status}.", "success")
    conn.close()
    return redirect(url_for('extension.manage_farmers'))



@extension_bp.route('/farmers/pending', methods=['GET'])
@login_required
def pending_farmers():
    if current_user.role != 'extension_worker':
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, email, district, crop, created_at 
        FROM users WHERE role='farmer' AND status='pending'
        ORDER BY created_at DESC
    """)
    farmers = cursor.fetchall()
    conn.close()

    return render_template('farmer_management/extension_pending_farmers.html', farmers=farmers)


@extension_bp.route('/farmers/approve/<int:farmer_id>', methods=['POST'])
@login_required
def approve_farmer(farmer_id):
    if current_user.role != 'extension_worker':
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='active' WHERE id=? AND role='farmer'", (farmer_id,))

    message = "Your agriconnect account has been approved by the Extension Worker. You can now access all features."
    cursor.execute("INSERT INTO notifications (user_id, message, created_at) VALUES (?, ?, ?)", (farmer_id, message, created_at))

    conn.commit()
    conn.close()

    flash("Farmer approved successfully!", "success")
    return redirect(url_for('extension.pending_farmers'))
