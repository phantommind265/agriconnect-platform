import uuid
import io
import qrcode
from flask import Blueprint, request, session, redirect, url_for, render_template, send_file
import sqlite3
from datetime import datetime, timedelta
import os
from flask import current_app, flash
from flask import send_file, abort
from agriplatform.forms.agrishare import JoinSessionForm
from agriplatform.forms.agrishare_upload import UploadFileForm
from flask_login import current_user, login_required
from agriplatform.forms.agrishare_create import CreateShareSessionForm

UPLOAD_FOLDER = os.path.join("agriplatform", "static", "uploads", "agrishare")
DB_PATH = os.path.join("agriplatform", "agriconnect.db")
agrishare_bp = Blueprint('agrishare', __name__, url_prefix='/agrishare')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@agrishare_bp.route('/create', methods=['GET', 'POST'])
def create_share_session():

    form = CreateShareSessionForm()

    if form.validate_on_submit():
        flash('Session closed (functionality to implement).')
        return redirect(url_for('auth.farmer_dashboard'))

    session_id = str(uuid.uuid4())

    created_at = datetime.now()
    expires_at = created_at + timedelta(minutes=15)

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO share_sessions (session_id, owner_user_id, created_at, expires_at, status) VALUES (?, ?, ?, ?, ?)',
        (session_id, current_user.id, created_at, expires_at, 'active')
    )
    conn.commit()
    conn.close()

    share_url = url_for('agrishare.connect_share_session', session_id=session_id, _external=True)

    import base64
    qr_img = qrcode.make(share_url)
    img_io = io.BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    qr_base64 = base64.b64encode(img_io.getvalue()).decode('ascii')

    return render_template('agrishare_create.html', qr_base64=qr_base64, share_url=share_url, form=form)


@agrishare_bp.route('/join', methods=['GET', 'POST'])
def join_session():
    form = JoinSessionForm()

    if form.validate_on_submit():
        session_url_or_id = form.session_value.data.strip()

        # If full URL is pasted, extract session ID
        if session_url_or_id.startswith('http'):
            try:
                session_id = session_url_or_id.rstrip('/').split('/')[-1]
            except:
                session_id = None
        else:
            session_id = session_url_or_id

        if session_id:
            return redirect(url_for('agrishare.connect_share_session', session_id=session_id))

    return render_template('agrishare_join.html', form=form)


@agrishare_bp.route('/download/<int:file_id>')
def download_file(file_id):
    conn = get_db_connection()
    file_record = conn.execute('SELECT * FROM shared_files WHERE id = ?', (file_id,)).fetchone()
    conn.close()

    if file_record is None:
        abort(404)

    return send_file(file_record['filepath'], as_attachment=True, download_name=file_record['filename'])

@agrishare_bp.route('/connect/<session_id>', methods=['GET'])
def connect_share_session(session_id):
    form = UploadFileForm() 

    conn = get_db_connection()
    session_data = conn.execute(
        'SELECT * FROM share_sessions WHERE session_id = ? AND status = ?',
        (session_id, 'active')
    ).fetchone()

    files = conn.execute(
        'SELECT * FROM shared_files WHERE session_id = ?',
        (session_id,)
    ).fetchall()

    conn.close()

    if session_data is None:
        return "<h3>Invalid or expired share session.</h3>", 404

    return render_template('agrishare_connect.html', session_id=session_id, files=files, form=form)


@agrishare_bp.route('/upload/<session_id>', methods=['POST'])
def upload_file(session_id):
    #if 'user_id' not in session:
     #   return redirect(url_for('auth.login'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('agrishare.connect_share_session', session_id=session_id))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('agrishare.connect_share_session', session_id=session_id))

    if file:
        #user_id = session['user_id']

        # Secure filename
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)

        # Create directory if not exists
        save_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER, session_id)
        os.makedirs(save_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(save_dir, filename)
        file.save(filepath)

        # Save file info to DB
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO shared_files (session_id, filename, filepath, uploaded_by) VALUES (?, ?, ?, ?)',
            (session_id, filename, filepath, current_user.id)
        )
        conn.commit()
        conn.close()

        flash('File uploaded successfully')
        return redirect(url_for('agrishare.connect_share_session', session_id=session_id))

