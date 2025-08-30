from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import os
from app.forms.market_form import MarketItemForm
from werkzeug.utils import secure_filename
from flask_login import login_required


UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
marketplace_bp = Blueprint('marketplace', __name__)
DB_PATH = os.path.join("app", "agriconnect.db")

@marketplace_bp.route('/marketplace', methods=['GET', 'POST'])
@login_required
def market_page():
    form = MarketItemForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market_items (title, price, description, category,
        seller_name, contact_info)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            form.title.data,
            form.price.data,
            form.description.data,
            form.category.data,
            form.seller_name.data,
            form.contact_info.data
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('marketplace.market_page'))

    #load all items
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM market_items ORDER BY datetime(created_at) DESC")
    items = cursor.fetchall()
    conn.close()

    #handle search/filter
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM market_items WHERE 1=1"
    params = []

    if query:
        sql += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])

    if category:
        sql += " AND category = ?"
        params.append(category)

    cursor.execute(sql, params)
    items = cursor.fetchall()
    conn.close()

    return render_template('market_place.html', form=form, items=items)


@marketplace_bp.route('/marketplace/add', methods=['GET', 'POST'])
def add_item():
    form = MarketItemForm()

    if form.validate_on_submit():
        image = form.image.data
        image_filename = None

        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO market_items (title, price, description, category,
        seller_name, contact_info, image_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            form.title.data,
            form.price.data,
            form.description.data,
            form.category.data,
            form.seller_name.data,
            form.contact_info.data,
            image_filename
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('marketplace.market_page'))
    return render_template('add_item.html', form=form)

    title = request.form.get('title')
    price = request.form.get('price')
    description = request.form.get('description')
    category = request.form.get('category')
    seller_name = request.form.get('seller_name')
    contact_info = request.form.get('contact_info')

    #handle image
    image_file = request.files.get('image')
    image_filename = None

    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        image_filename = filename

    #insert into database
    form = MarketItemForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market_items (title, price, description, category, seller_name, contact_info, image_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, price, description, category, seller_name, contact_info, image_filename))
        conn.commit()
        conn.close()
        return redirect(url_for('marketplace.market_page'))

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@marketplace_bp.route('/marketplace/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM market_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('marketplace.market_page'))
