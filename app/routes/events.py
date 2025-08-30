from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3, os
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms.event_form import EventForm

DB_PATH = os.path.join("app", "agriconnect.db")
events_bp = Blueprint('events_bp', __name__)
UPLOAD_FOLDER = 'static/uploads/events'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# View all events
@events_bp.route('/events')
def view_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY date ASC")
    events = cursor.fetchall()
    conn.close()
    return render_template('events/view_event.html', events=events)

# Add new event
@events_bp.route('/events/add', methods=['GET', 'POST'])
def add_event():
    form = EventForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        location = form.location.data
        date = form.date.data
        time = form.time.data
        organizer = form.organizer.data

        flyer_path = None
        if form.flyer.data:
            filename = secure_filename(form.flyer.data.filename)
            flyer_path = os.path.join(UPLOAD_FOLDER, filename)
            form.flyer.data.save(flyer_path)

        conn = get_db()
        conn.execute("""
            INSERT INTO events (title, description, location, date, time, organizer, flyer_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, location, str(date), str(time), organizer, flyer_path))
        conn.commit()
        conn.close()

        flash("Event added successfully!", "success")
        return redirect(url_for('events_bp.view_events'))

    return render_template('events/add_event.html', form=form)

@events_bp.route('/events/register/<int:event_id>', methods=['POST'])
def register_event(event_id):
    conn = get_db()
    cursor = conn.cursor()

    # Check if already registered
    cursor.execute("SELECT * FROM event_registrations WHERE user_id=? AND event_id=?", 
                   (current_user.id, event_id))
    if cursor.fetchone():
        flash("You have already registered for this event.", "warning")
        return redirect(url_for('events.view_events'))

    cursor.execute("INSERT INTO event_registrations (current_user.id, event_id) VALUES (?, ?)", 
                   (current_user.id, event_id))
    conn.commit()

    # Fetch user email and event details
    cursor.execute("SELECT email FROM users WHERE id=?", (current_user.id,))
    user_email = cursor.fetchone()['email']

    cursor.execute("SELECT title, date, location FROM events WHERE id=?", (event_id,))
    event = cursor.fetchone()

    # Send confirmation email
    from flask_mail import Message
    from app import mail  # assuming you set up Flask-Mail

    msg = Message(
        subject=f"Event Registration Confirmation - {event['title']}",
        recipients=[user_email]
    )
    msg.body = f"""
    Hello,

    You have successfully registered for the event:
    Title: {event['title']}
    Date: {event['date']}
    Location: {event['location']}

    We look forward to seeing you there!
    """
    mail.send(msg)

    flash("You have successfully registered! A confirmation email has been sent.", "success")
    return redirect(url_for('events.view_events'))

#admin event atendees
@events_bp.route('/events/<int:event_id>/attendees')
def event_attendees(event_id):
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for('events.view_events'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.username, u.email
        FROM event_registrations r
        INNER JOIN users u ON r.user_id = u.id
        WHERE r.event_id = ?
    """, (event_id,))
    attendees = cursor.fetchall()

    cursor.execute("SELECT title FROM events WHERE id=?", (event_id,))
    event_title = cursor.fetchone()['title']

    return render_template('events/attendees.html', attendees=attendees, event_title=event_title)


@events_bp.route('/events/my')
def my_events():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.id, e.title, e.description, e.date, e.location, e.flyer_path
        FROM events e
        INNER JOIN event_registrations r ON e.id = r.event_id
        WHERE r.user_id = ?
        ORDER BY e.date ASC
    """, (current_user.id,))
    my_events_list = cursor.fetchall()

    return render_template('events/my_events.html', events=my_events_list)
