import sqlite3
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.field_form import FieldForm, CropForm
import os

field_bp = Blueprint("field", __name__)

DB_PATH = os.path.join("app", "agriconnect.db")

@field_bp.route("/my-fields", methods=["GET", "POST"])
@login_required
def my_fields():
    form = FieldForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fields (user_id, name, size, location)
            VALUES (?, ?, ?, ?)
        """, (current_user.id, form.name.data, form.size.data, form.location.data))
        conn.commit()
        conn.close()

        flash("✅ Field added successfully!", "success")
        return redirect(url_for("field.view_fields"))

    # Fetch existing fields for this user
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, size, location, created_at FROM fields WHERE user_id = ?", (current_user.id,))
    fields = cursor.fetchall()
    conn.close()

    return render_template("farmer/my_fields.html", form=form)

@field_bp.route("/active-crops")
@login_required
def active_crops():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT crops.id, crops.name, crops.season, crops.expected_yield, crops.planted_at, fields.name
        FROM crops
        JOIN fields ON crops.field_id = fields.id
        WHERE fields.user_id = ?
        ORDER BY crops.planted_at DESC
    """, (current_user.id,))
    crops = cursor.fetchall()
    conn.close()
    return render_template("farmer/active_crops.html", crops=crops)

@field_bp.route("/fields")
@login_required
def view_fields():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, size, location, created_at FROM fields WHERE user_id = ?",
                   (current_user.id,))
    fields = cursor.fetchall()
    conn.close()
    return render_template("farmer/active_fields.html", fields=fields)


@field_bp.route("/my-crops", methods=["GET", "POST"])
@login_required
def my_crops():
    form = CropForm()

    # Load fields for this farmer into the dropdown
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM fields WHERE user_id = ?", (current_user.id,))
    user_fields = cursor.fetchall()
    conn.close()

    form.field_id.choices = [(f[0], f[1]) for f in user_fields]

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO crops (field_id, name, season, expected_yield)
            VALUES (?, ?, ?, ?)
        """, (form.field_id.data, form.name.data, form.season.data, form.expected_yield.data))
        conn.commit()
        conn.close()

        flash("✅ Crop added successfully!", "success")
        return redirect(url_for("field.my_crops"))

    # Fetch crops belonging to this farmer (join crops + fields)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT crops.id, crops.name, crops.season, crops.expected_yield, crops.planted_at, fields.name
        FROM crops
        JOIN fields ON crops.field_id = fields.id
        WHERE fields.user_id = ?
    """, (current_user.id,))
    crops = cursor.fetchall()
    conn.close()

    return render_template("farmer/my_crops.html", form=form, crops=crops)


@field_bp.route("/field/<int:field_id>/edit", methods=["GET", "POST"])
@login_required
def edit_field(field_id):
    form = FieldForm()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, size, location FROM fields WHERE id = ? AND user_id = ?", (field_id, current_user.id))
    field = cursor.fetchone()

    if not field:
        flash("❌ Field not found or unauthorized.", "danger")
        conn.close()
        return redirect(url_for("field.view_fields"))

    if request.method == "GET":
        form.name.data = field[1]
        form.size.data = field[2]
        form.location.data = field[3]

    if form.validate_on_submit():
        cursor.execute("""
            UPDATE fields SET name=?, size=?, location=? WHERE id=? AND user_id=?
        """, (form.name.data, form.size.data, form.location.data, field_id, current_user.id))
        conn.commit()
        conn.close()
        flash("✅ Field updated successfully!", "success")
        return redirect(url_for("field.view_fields"))

    conn.close()
    return render_template("farmer/edit_field.html", form=form)


@field_bp.route("/field/<int:field_id>/delete", methods=["POST"])
@login_required
def delete_field(field_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fields WHERE id=? AND user_id=?", (field_id, current_user.id))
    conn.commit()
    conn.close()
    flash("🗑️ Field deleted successfully!", "info")
    return redirect(url_for("field.my_fields"))


@field_bp.route("/crop/<int:crop_id>/edit", methods=["GET", "POST"])
@login_required
def edit_crop(crop_id):
    form = CropForm()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load crop
    cursor.execute("""
        SELECT crops.id, crops.name, crops.season, crops.expected_yield, crops.field_id
        FROM crops
        JOIN fields ON crops.field_id = fields.id
        WHERE crops.id = ? AND fields.user_id = ?
    """, (crop_id, current_user.id))
    crop = cursor.fetchone()

    if not crop:
        flash("❌ Crop not found or unauthorized.", "danger")
        conn.close()
        return redirect(url_for("farmer.my_crops"))

    # Populate dropdown fields
    cursor.execute("SELECT id, name FROM fields WHERE user_id = ?", (current_user.id,))
    user_fields = cursor.fetchall()
    form.field_id.choices = [(f[0], f[1]) for f in user_fields]

    if request.method == "GET":
        form.name.data = crop[1]
        form.season.data = crop[2]
        form.expected_yield.data = crop[3]
        form.field_id.data = crop[4]

    if form.validate_on_submit():
        cursor.execute("""
            UPDATE crops SET name=?, season=?, expected_yield=?, field_id=? WHERE id=?
        """, (form.name.data, form.season.data, form.expected_yield.data, form.field_id.data, crop_id))
        conn.commit()
        conn.close()
        flash("✅ Crop updated successfully!", "success")
        return redirect(url_for("field.my_crops"))

    conn.close()
    return render_template("farmer/edit_crop.html", form=form)



@field_bp.route("/crop/<int:crop_id>/delete", methods=["POST"])
@login_required
def delete_crop(crop_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM crops
        WHERE id=? AND field_id IN (SELECT id FROM fields WHERE user_id=?)
    """, (crop_id, current_user.id))
    conn.commit()
    conn.close()
    flash("🗑️ Crop deleted successfully!", "info")
    return redirect(url_for("field.my_crops"))
