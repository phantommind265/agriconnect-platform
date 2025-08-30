import os
import sqlite3
from decimal import Decimal
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms.equipment_form import EquipmentForm
from app.forms.availability_form import AvailabilityForm
from app.forms.booking_form import BookingForm
from app.forms.log_form import MaintenanceForm

equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')


DB_PATH = os.path.join("app", "agriconnect.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@equipment_bp.route('/Register', methods=['GET', 'POST'])
def register_equipment():
    #user_id = session.get('user_id')
    #if not user_id:
     #   flash("Please log in to register your equipment.", "danger")
      #  return redirect(url_for('auth.login'))

    form = EquipmentForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(image_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO equipment (name, type, model, condition, location, image_filename, owner_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            form.name.data,
            form.type.data,
            form.model.data,
            form.condition.data,
            form.location.data,
            filename,
            current_user.id
        ))
        conn.commit()
        conn.close()

        flash("Equipment registered successfully!", "success")
        return redirect(url_for('equipment.list_equipment'))

    return render_template('register_equipment.html', form=form)

@equipment_bp.route('/list')
def list_equipment():
    #user_id = session.get('user_id')
    #if not user_id:
     #   flash("Please log in to see your list of equipments")
      #  return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment WHERE owner_id = ?", (current_user.id,))
    equipments = cursor.fetchall()
    conn.close()
    return render_template('list_equipment.html', equipments=equipments)

@equipment_bp.route('/<int:equipment_id>/availability', methods=['GET', 'POST'])
def availability(equipment_id):
    #user_id = session.get('user_id')
    #if not user_id:
     #   flash("Please log in to see your list of equipments")
      #  return redirect(url_for('auth.login'))

    form = AvailabilityForm()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM equipment WHERE id=? AND owner_id=?", (equipment_id, current_user.id))
    equipment = cursor.fetchone()
    if not equipment:
        conn.close()
        flash("You do not own this equipment.", "danger")
        return redirect(url_for('equipment.list_equipment'))

    if form.validate_on_submit():
        date = form.date.data.strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO equipment_availability (equipment_id, date, status)
            VALUES (?, ?, 'unavailable')
        """, (equipment_id, date))
        conn.commit()
        flash("Date marked as unavailable.", "success")

    # Fetch all unavailable dates for this equipment
    cursor.execute("SELECT date FROM equipment_availability WHERE equipment_id=?", (equipment_id,))
    unavailable_dates = [row['date'] for row in cursor.fetchall()]
    conn.close()

    return render_template('availability.html', form=form, equipment=equipment, unavailable_dates=unavailable_dates)

@equipment_bp.route('/<int:equipment_id>/book', methods=['GET', 'POST'])
@login_required
def request_booking(equipment_id):
    form = BookingForm()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM equipment WHERE id=?", (equipment_id,))
    equipment = cursor.fetchone()

    if not equipment:
        flash("Equipment not found", "danger")
        conn.close()
        return redirect(url_for('equipment.equipment_list'))

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        # Check availability
        cursor.execute("""
            SELECT * FROM equipment_availability
            WHERE equipment_id=? AND date BETWEEN ? AND ? AND status='unavailable'
        """, (equipment_id, start_date, end_date))
        unavailable_dates = cursor.fetchall()

        if unavailable_dates:
            flash("Equipment is unavailable on some selected dates", "danger")
        else:
            cursor.execute("""
                INSERT INTO equipment_bookings (equipment_id, user_id, start_date, end_date)
                VALUES (?, ?, ?, ?)
            """, (equipment_id, current_user.id, start_date, end_date))
            conn.commit()
            flash("Booking request submitted", "success")
            return redirect(url_for('equipment.list_equipment'))

    conn.close()
    return render_template('booking_request.html', form=form, equipment=equipment)


@equipment_bp.route('/<int:equipment_id>/maintenance', methods=['GET', 'POST'])
def maintenance_log(equipment_id):
    form = MaintenanceForm()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if equipment exists
    cursor.execute("SELECT id, name FROM equipment WHERE id=?", (equipment_id,))
    equipment = cursor.fetchone()
    if not equipment:
        flash("Equipment not found", "danger")
        return redirect(url_for('equipment.list_equipment'))

    if form.validate_on_submit():
        description = form.description.data
        date = form.date.data
        cost = float(form.cost.data) if form.cost.data else None

        cursor.execute('''
            INSERT INTO equipment_maintenance (equipment_id, description, date, cost)
            VALUES (?, ?, ?, ?)
        ''', (equipment_id, description, date, cost))
        conn.commit()
        flash("Maintenance log added", "success")
        return redirect(url_for('equipment.maintenance_log', equipment_id=equipment_id))

    # Fetch logs
    cursor.execute('''
        SELECT description, date, cost FROM equipment_maintenance
        WHERE equipment_id=? ORDER BY date DESC
    ''', (equipment_id,))
    logs = cursor.fetchall()

    conn.close()
    return render_template('maintenance_log.html', form=form, equipment=equipment, logs=logs)


@equipment_bp.route('/usage_analytics')
def usage_analytics():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all equipment owned by current user
    cursor.execute("SELECT id, name FROM equipment WHERE owner_id=?", (current_user.id,))
    equipments = cursor.fetchall()

    analytics = []

    for eq in equipments:
        eq_id = eq['id']

        # Count bookings
        cursor.execute("""
            SELECT COUNT(*) as bookings_count,
                   SUM(julianday(end_date) - julianday(start_date) + 1) as booked_days
            FROM equipment_bookings
            WHERE equipment_id=? AND status='approved'
        """, (eq_id,))
        booking_stats = cursor.fetchone()

        # Count maintenance logs
        cursor.execute("""
            SELECT COUNT(*) as maintenance_count
            FROM equipment_maintenance
            WHERE equipment_id=?
        """, (eq_id,))
        maintenance_stats = cursor.fetchone()

        analytics.append({
            'equipment': eq['name'],
            'bookings_count': booking_stats['bookings_count'] or 0,
            'booked_days': int(booking_stats['booked_days'] or 0),
            'maintenance_count': maintenance_stats['maintenance_count'] or 0
        })

    conn.close()

    return render_template('usage_analytics.html', analytics=analytics)

@equipment_bp.route('/marketplace', methods=['GET'])
def marketplace():
    search = request.args.get('search', '').strip()
    filter_type = request.args.get('type', '').strip()
    filter_location = request.args.get('location', '').strip()

    query = '''
        SELECT e.id, e.name, e.type, e.model, e.condition, e.location, e.image_filename, u.username
        FROM equipment e
        JOIN users u ON e.owner_id = u.id
        WHERE 1=1
    '''
    params = []

    if search:
        query += " AND (e.name LIKE ? OR e.model LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])

    if filter_type:
        query += " AND e.type = ?"
        params.append(filter_type)

    if filter_location:
        query += " AND e.location = ?"
        params.append(filter_location)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    equipments = cursor.fetchall()
    conn.close()

    return render_template('equipment_marketplace.html', equipments=equipments, search=search, filter_type=filter_type, filter_location=filter_location)

