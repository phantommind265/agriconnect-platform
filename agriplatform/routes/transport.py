from flask import Blueprint, render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user
import sqlite3
import os
from datetime import datetime
from agriplatform.forms.transport_form import TransportListingForm, BookTransportForm

transport_bp = Blueprint("transport", __name__)

DB_PATH = os.path.join("agriplatform", "agriconnect.db")

@transport_bp.route("/transport/new", methods=["GET", "POST"])
@login_required
def new_transport():
    form = TransportListingForm()
    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transport_listings 
            (owner_id, vehicle_type, capacity, route, available_date, price, contact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            current_user.id,
            form.vehicle_type.data,
            form.capacity.data,
            form.route.data,
            form.available_date.data.strftime('%Y-%m-%d'),
            form.price.data,
            form.contact.data,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        conn.close()
        flash("🚚 Transport listing posted successfully!", "success")
        return redirect(url_for("transport.list_transport"))
    return render_template("new_transport.html", form=form)


@transport_bp.route("/transport", methods=["GET"])
@login_required
def list_transport():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, vehicle_type, capacity, route, available_date, price, contact, created_at
        FROM transport_listings
        ORDER BY available_date ASC
    """)
    listings = cursor.fetchall()
    conn.close()

    forms = {l[0]: BookTransportForm(prefix=str(l[0])) for l in listings}
    return render_template("list_transport.html", listings=listings, forms=forms)


@transport_bp.route("/transport/book/<int:listing_id>", methods=["POST"])
@login_required
def book_transport(listing_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Record a booking for the current user
    cursor.execute("""
        INSERT INTO transport_bookings (listing_id, farmer_id, created_at)
        VALUES (?, ?, ?)
    """, (listing_id, current_user.id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    flash("✅ You have successfully booked this transport!", "success")
    return redirect(url_for("transport.list_transport"))



@transport_bp.route("/transport/my_bookings")
@login_required
def my_bookings():
    """Show all bookings for the current user's transport listings."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get bookings for listings owned by the current user
    cursor.execute("""
        SELECT b.id, t.vehicle_type, t.route, t.available_date,
               u.username, b.status, b.created_at
        FROM transport_bookings b
        JOIN transport_listings t ON b.listing_id = t.id
        JOIN users u ON b.farmer_id = u.id
        WHERE t.owner_id = ?
        ORDER BY b.created_at DESC
    """, (current_user.id,))
    bookings = cursor.fetchall()
    conn.close()

    return render_template("transport/my_bookings.html", bookings=bookings)


@transport_bp.route("/transport/update_status/<int:booking_id>/<string:new_status>", methods=["POST"])
@login_required
def update_booking_status(booking_id, new_status):
    valid_statuses = ["pending", "confirmed", "completed"]
    if new_status not in valid_statuses:
        flash("❌ Invalid status.", "danger")
        return redirect(url_for("transport.my_bookings"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verify that the booking belongs to the current user's listing
    cursor.execute("""
        SELECT t.owner_id, b.id
        FROM transport_bookings b
        JOIN transport_listings t ON b.listing_id = t.id
        WHERE b.id = ?
    """, (booking_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        flash("❌ Booking not found.", "danger")
        return redirect(url_for("transport.my_bookings"))


    owner_id, booked_user_id = row
    if owner_id != current_user.id:
        conn.close()
        flash("❌ Unauthorized to update this booking.", "danger")
        return redirect(url_for("transport.my_bookings"))

    # Update the status
    cursor.execute("""
        UPDATE transport_bookings
        SET status = ?
        WHERE id = ?
    """, (new_status, booking_id))

    msg = f"Your transport booking has been {new_status}."
    cursor.execute("""
        INSERT INTO notifications (user_id, message, is_read, created_at)
        VALUES (?, ?, 0, datetime('now'))
    """, (booked_user_id, msg))
    conn.commit()
    conn.close()

    flash(f"✅ Booking status updated to '{new_status}' and notification sent.", "success")
    return redirect(url_for("transport.my_bookings"))

