from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3
import os
from agriplatform.forms.field_data_form import FieldDataForm

DB_PATH = os.path.join("agriplatform", "agriconnect.db")
collection_bp = Blueprint('collection', __name__, template_folder='templates/extension')

def is_extension():
    return current_user.role == 'extension_worker'

@collection_bp.route('/data/new', methods=['GET', 'POST'])
@login_required
def add_field_data():
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    form = FieldDataForm()
    if form.validate_on_submit():
        farmer_id = form.farmer_id.data if form.farmer_id.data else None
        district = form.district.data.strip()
        crop = form.crop.data.strip()
        observation = form.observation.data.strip()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO field_data (worker_id, farmer_id, district, crop, observation)
            VALUES (?, ?, ?, ?, ?)
        """, (current_user.id, farmer_id, district, crop, observation))
        conn.commit()
        conn.close()

        flash("Field data recorded successfully!", "success")
        return redirect(url_for('collection.view_field_data'))

    return render_template('data_collection.html', form=form)


@collection_bp.route('/data/edit/<int:data_id>', methods=['GET', 'POST'])
@login_required
def edit_field_data(data_id):
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch entry
    cursor.execute("SELECT * FROM field_data WHERE id=?", (data_id,))
    entry = cursor.fetchone()
    if not entry:
        conn.close()
        abort(404)

    form = FieldDataForm(
        farmer_id=entry['farmer_id'],
        district=entry['district'],
        crop=entry['crop'],
        observation=entry['observation']
    )

    if form.validate_on_submit():
        farmer_id = form.farmer_id.data if form.farmer_id.data else None
        district = form.district.data.strip()
        crop = form.crop.data.strip()
        observation = form.observation.data.strip()

        cursor.execute("""
            UPDATE field_data
            SET farmer_id=?, district=?, crop=?, observation=?
            WHERE id=?
        """, (farmer_id, district, crop, observation, data_id))
        conn.commit()
        conn.close()

        flash("Field data updated successfully!", "success")
        return redirect(url_for('collection.view_field_data'))

    conn.close()
    return render_template('data_collection.html', form=form)

# Delete field data
@collection_bp.route('/data/delete/<int:data_id>', methods=['POST'])
@login_required
def delete_field_data(data_id):
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM field_data WHERE id=?", (data_id,))
    conn.commit()
    conn.close()

    flash("Field data deleted successfully!", "success")
    return redirect(url_for('collection.view_field_data'))


@collection_bp.route('/data', methods=['GET', 'POST'])
@login_required
def view_field_data():
    if not is_extension():
        flash("Access denied: Extension Workers only.", "danger")
        return redirect(url_for('auth.login'))

    # --- Pagination setup ---
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Records per page
    offset = (page - 1) * per_page

    # --- Filtering setup ---
    district_filter = request.args.get('district', '').strip()
    crop_filter = request.args.get('crop', '').strip()
    query = """
        SELECT f.id, f.district, f.crop, f.observation, f.date_collected,
               u.username AS worker_name
        FROM field_data f
        JOIN users u ON f.worker_id = u.id
        WHERE 1=1
    """
    params = []

    if district_filter:
        query += " AND f.district LIKE ?"
        params.append(f"%{district_filter}%")

    if crop_filter:
        query += " AND f.crop LIKE ?"
        params.append(f"%{crop_filter}%")

    # Count total for pagination
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query.replace("SELECT f.id, f.district, f.crop, f.observation, f.date_collected,\n               u.username AS worker_name", "SELECT COUNT(*)"), params)
    total_records = cursor.fetchone()[0]

    # Fetch paginated data
    query += " ORDER BY f.date_collected DESC LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    cursor.execute(query, params)
    data_entries = cursor.fetchall()
    conn.close()

    total_pages = (total_records + per_page - 1) // per_page

    return render_template(
        'data_records.html',
        data_entries=data_entries,
        page=page,
        total_pages=total_pages,
        district_filter=district_filter,
        crop_filter=crop_filter
    )
