import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from agriplatform.forms.warehouse_form import WarehouseListingForm, BookWarehouseForm, StatusForm
import os

DB_PATH = os.path.join("agriplatform", "agriconnect.db")
warehouse_bp = Blueprint("warehouse", __name__)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@warehouse_bp.route("/warehouse/add", methods=["GET", "POST"])
@login_required
def add_warehouse():
    form = WarehouseListingForm()
    if form.validate_on_submit():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO warehouse_listings (owner_id, location, capacity, price_per_day, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            current_user.id,
            form.location.data,
            form.capacity.data,
            form.price_per_day.data,
            form.description.data,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        flash("✅ Warehouse added successfully.", "success")
        return redirect(url_for("warehouse.view_warehouses"))
    return render_template("warehouse/add_warehouse.html", form=form)


@warehouse_bp.route("/warehouse", methods=["GET"])
@login_required
def view_warehouses():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT w.id, w.location, w.capacity, w.price_per_day, w.description, u.username AS owner, w.created_at
        FROM warehouse_listings w
        JOIN users u ON w.owner_id = u.id
        ORDER BY w.created_at DESC
    """)
    listings = cur.fetchall()
    conn.close()

    # Create a BookWarehouseForm instance per listing (prefix = listing id)
    forms = {row["id"]: BookWarehouseForm(prefix=f"book-{row['id']}") for row in listings}
    return render_template("warehouse/view_warehouses.html", listings=listings, forms=forms)

'''
@warehouse_bp.route("/warehouse/book/<int:listing_id>", methods=["POST"])
@login_required
def book_warehouse(listing_id):
    form = BookWarehouseForm(prefix=f"book-{listing_id}")
    if not form.validate_on_submit():
        # If validation fails, flash and redirect back (you can improve error messaging)
        flash("Please provide valid booking dates (YYYY-MM-DD).", "danger")
        return redirect(url_for("warehouse.view_warehouses"))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO warehouse_bookings (listing_id, user_id, status, booked_from, booked_to, created_at)
        VALUES (?, ?, 'pending', ?, ?, ?)
    """, (
        listing_id,
        current_user.id,
        form.booked_from.data.strftime("%Y-%m-%d"),
        form.booked_to.data.strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

    flash("✅ Warehouse booked successfully. Waiting for owner confirmation.", "success")
    return redirect(url_for("warehouse.view_warehouses"))
'''

@warehouse_bp.route("/warehouse/book/<int:listing_id>", methods=["POST"])
@login_required
def book_warehouse(listing_id):
    form = BookWarehouseForm(prefix=f"book-{listing_id}")
    if not form.validate_on_submit():
        flash("Please provide valid booking dates (YYYY-MM-DD).", "danger")
        return redirect(url_for("warehouse.view_warehouses"))

    conn = get_conn()
    cur = conn.cursor()

    # Get owner id for notification
    cur.execute("SELECT owner_id, location FROM warehouse_listings WHERE id = ?", (listing_id,))
    listing = cur.fetchone()
    if not listing:
        conn.close()
        flash("Warehouse listing not found.", "danger")
        return redirect(url_for("warehouse.view_warehouses"))

    cur.execute("""
        INSERT INTO warehouse_bookings (listing_id, user_id, status, booked_from, booked_to, created_at)
        VALUES (?, ?, 'pending', ?, ?, ?)
    """, (
        listing_id,
        current_user.id,
        form.booked_from.data.strftime("%Y-%m-%d"),
        form.booked_to.data.strftime("%Y-%m-%d"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    # 🔔 Insert notification for the warehouse owner
    try:
        message = f"{current_user.username} booked your warehouse at {listing['location']}."
        cur.execute("""
            INSERT INTO notifications (user_id, title, message, link, is_read, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (
            listing["owner_id"],
            "New Warehouse Booking",
            message,
            url_for('warehouse.owner_warehouse_bookings'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    except Exception as e:
        # Fail silently if notifications table doesn't exist
        print(f"Notification insert failed: {e}")

    conn.commit()
    conn.close()

    flash("✅ Warehouse booked successfully. Waiting for owner confirmation.", "success")
    return redirect(url_for("warehouse.view_warehouses"))



@warehouse_bp.route("/warehouse/my_bookings", methods=["GET"])
@login_required
def my_warehouse_bookings():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, w.location, b.booked_from, b.booked_to, b.status, b.created_at
        FROM warehouse_bookings b
        JOIN warehouse_listings w ON b.listing_id = w.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    """, (current_user.id,))
    bookings = cur.fetchall()
    conn.close()
    return render_template("warehouse/my_warehouse_bookings.html", bookings=bookings)


@warehouse_bp.route("/warehouse/owner_bookings", methods=["GET"])
@login_required
def owner_warehouse_bookings():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, u.username as booker, w.location, b.booked_from, b.booked_to, b.status, b.created_at
        FROM warehouse_bookings b
        JOIN warehouse_listings w ON b.listing_id = w.id
        JOIN users u ON b.user_id = u.id
        WHERE w.owner_id = ?
        ORDER BY b.created_at DESC
    """, (current_user.id,))
    bookings = cur.fetchall()
    conn.close()

    # one StatusForm per booking for CSRF
    forms = {row["id"]: StatusForm(prefix=f"status-{row['id']}") for row in bookings}
    return render_template("warehouse/owner_warehouse_bookings.html", bookings=bookings, forms=forms)


@warehouse_bp.route("/warehouse/update_status/<int:booking_id>/<string:new_status>", methods=["POST"])
@login_required
def update_warehouse_booking_status(booking_id, new_status):
    valid_statuses = ["pending", "confirmed", "completed"]
    if new_status not in valid_statuses:
        flash("Invalid status.", "danger")
        return redirect(url_for("warehouse.owner_warehouse_bookings"))

    # validate CSRF: use the StatusForm prefix matching this booking id
    form = StatusForm(prefix=f"status-{booking_id}")
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("warehouse.owner_warehouse_bookings"))

    conn = get_conn()
    cur = conn.cursor()

    # Check owner of the listing
    cur.execute("""
        SELECT w.owner_id, b.user_id
        FROM warehouse_bookings b
        JOIN warehouse_listings w ON b.listing_id = w.id
        WHERE b.id = ?
    """, (booking_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        flash("Booking not found.", "danger")
        return redirect(url_for("warehouse.owner_warehouse_bookings"))

    owner_id = row["owner_id"]
    booked_user_id = row["user_id"]
    if owner_id != current_user.id:
        conn.close()
        flash("Unauthorized to update this booking.", "danger")
        return redirect(url_for("warehouse.owner_warehouse_bookings"))

    # Update status
    cur.execute("UPDATE warehouse_bookings SET status = ? WHERE id = ?", (new_status, booking_id))

    # Insert notification to the user who booked (if you have notifications table)
    try:
        msg = f"Your warehouse booking (id {booking_id}) has been {new_status}."
        cur.execute("""
            INSERT INTO notifications (user_id, title, message, link, is_read, created_at)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (booked_user_id, "Warehouse Booking Update", msg, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except Exception:
        # If notifications table doesn't exist or fails, ignore but keep booking update
        pass

    conn.commit()
    conn.close()

    flash(f"Booking status updated to '{new_status}'.", "success")
    return redirect(url_for("warehouse.owner_warehouse_bookings"))


