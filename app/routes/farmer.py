from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms.profile_form import ProfileForm

farmer_bp = Blueprint('farmer', __name__)
UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "profiles")
ALLOWED_EXTENSIOND = {'jpg', 'jpeg', 'png', 'gif'}
DB_PATH = os.path.join("app", "agriconnect.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@farmer_bp.route('/farmers/profile')
def view_profile():
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM farmer_profiles WHERE user_id = ?', (current_user.id,)).fetchone()
    conn.close()

    return render_template('farmer/profile.html', profile=profile)

@farmer_bp.route('/farmers/all')
def all_farmers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM farmer_profiles")
    profiles = cursor.fetchall()

    return render_template('farmer/all_farmers.html', profiles=profiles)

@farmer_bp.route('/farmers/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    form = ProfileForm()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM farmer_profiles WHERE user_id = ?', (current_user.id,))
    row = cursor.fetchone()
    profile = dict(zip([column[0] for column in cursor.description], row)) if row else None

    if form.validate_on_submit():
        image_file = form.image.data
        filename = None

        if image_file:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(filepath)

        if profile:
            cursor.execute('''
                UPDATE farmer_profiles
                SET full_name = ?, farm_location = ?, contact_info = ?, crops = ?, animals = ?, bio = ?, image_filename = ?
                WHERE user_id = ?
            ''', (
                form.full_name.data,
                form.farm_location.data,
                form.contact_info.data,
                form.crops.data,
                form.animals.data,
                form.bio.data,
                filename or profile.get('image_filename'),
                current_user.id
            ))
        else:
            conn.execute('''
                INSERT INTO farmer_profiles (full_name, farm_location, contact_info, crops, animals, bio, image_filename, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                form.full_name.data, form.farm_location.data, form.contact_info.data, form.crops.data, form.animals.data, form.bio.data, filename, current_user.id
            ))
        conn.commit()
        conn.close()
        return redirect(url_for('farmer.view_profile'))
    conn.close()
    return render_template('farmer/edit_profile.html', form=form, profile=profile)
