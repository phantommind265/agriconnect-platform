from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import sqlite3
import os
from collections import defaultdict
from datetime import datetime

DB_PATH = os.path.join("agriplatform", "agriconnect.db")
extension_analytics_bp = Blueprint('extension_analytics', __name__, template_folder='templates')

def is_extension():
    return current_user.is_authenticated and current_user.role == 'extension_worker'

@extension_analytics_bp.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics_dashboard():
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    # --- Get filter values ---
    district_filter = request.args.get('district', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # --- Farmers per District ---
    query = "SELECT district, COUNT(*) AS count FROM users WHERE role='farmer'"
    params = []
    if district_filter:
        query += " AND district LIKE ?"
        params.append(f"%{district_filter}%")
    query += " GROUP BY district"
    cursor.execute(query, params)
    farmers_by_district = {row['district']: row['count'] for row in cursor.fetchall()}

    # --- Approved vs Pending ---
    cursor.execute("SELECT status, COUNT(*) AS count FROM users WHERE role='farmer' GROUP BY status")
    approval_counts = {'Approved': 0, 'Pending': 0}
    for row in cursor.fetchall():
        if row['status'] == 1:
            approval_counts['Approved'] = row['count']
        else:
            approval_counts['Pending'] = row['count']

    # --- Field Data per Crop ---
    query = "SELECT crop, COUNT(*) AS count FROM field_data WHERE 1=1"
    params = []
    if start_date:
        query += " AND date_collected >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date_collected <= ?"
        params.append(end_date)
    query += " GROUP BY crop"
    cursor.execute(query, params)
    records_per_crop = {row['crop']: row['count'] for row in cursor.fetchall()}

    # --- Monthly Trends ---
    query = """
        SELECT strftime('%Y-%m', date_collected) AS month, COUNT(*) AS count
        FROM field_data WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND date_collected >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date_collected <= ?"
        params.append(end_date)
    query += " GROUP BY month ORDER BY month ASC"
    cursor.execute(query, params)
    monthly_trends = {row['month']: row['count'] for row in cursor.fetchall()}

    conn.close()

    return render_template(
        'extension_analytics.html',
        farmers_by_district=farmers_by_district,
        approval_counts=approval_counts,
        records_per_crop=records_per_crop,
        monthly_trends=monthly_trends,
        district_filter=district_filter,
        start_date=start_date,
        end_date=end_date
    )

