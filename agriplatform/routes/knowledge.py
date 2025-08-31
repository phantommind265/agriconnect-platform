import os
import sqlite3
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from agriplatform.forms.knowledge_form import KnowledgeResourceForm

knowledge_bp = Blueprint('knowledge_bp', __name__, template_folder='templates')
DB_PATH = os.path.join("agriplatform", "agriconnect.db")
UPLOAD_FOLDER = os.path.join("agriplatform", "static", "uploads", "knowledge")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@knowledge_bp.route("/knowledge/add", methods=["GET", "POST"])
def add_knowledge():
    form = KnowledgeResourceForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        category = form.category.data
        file_path = None

        # Handle file upload if present
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            upload_folder =os.path.join(current_app.root_path, "static/uploads/knowledge")
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join("static/uploads/knowledge", filename)
            file.save(os.path.join(current_app.root_path, file_path))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO knowledge_resources (title, content, category, file_path)
            VALUES (?, ?, ?, ?)
        ''', (title, content, category, file_path))
        conn.commit()
        conn.close()

        flash("Knowledge resource added successfully!", "success")
        return redirect(url_for("knowledge_bp.view_knowledge"))

    return render_template("knowledge/add_knowledge.html", form=form)

@knowledge_bp.route("/knowledge", methods=["GET", "POST"])
def view_knowledge():
    conn = get_db()
    cursor = conn.cursor()

    search_query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()

    query = "SELECT * FROM knowledge_resources WHERE 1=1"
    params = []

    if search_query:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    cursor.execute(query, params)
    resources = cursor.fetchall()

    # get distinct categories for filter dropdown
    cursor.execute("SELECT DISTINCT category FROM knowledge_resources")
    categories = [row["category"] for row in cursor.fetchall() if row["category"]]

    conn.close()

    return render_template(
        "knowledge/view_knowledge.html",
        resources=resources,
        search_query=search_query,
        categories=categories,
        category_filter=category_filter,
    )

@knowledge_bp.route("/knowledge/<int:resource_id>")
def resource_detail(resource_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_resources WHERE id = ?", (resource_id,))
    resource = cursor.fetchone()
    conn.close()

    if not resource:
        return "Resource not found", 404

    return render_template("knowledge/resource_detail.html", resource=resource)


