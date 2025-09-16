import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user
from agriplatform.forms.report_form import ReportForm
import os
from flask import make_response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
DB_PATH = os.path.join("agriplatform", "agriconnect.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@reports_bp.teardown_app_request
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@reports_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_report():
    if current_user.role not in ["admin", "extension_worker"]:
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    # Fetch farmers to show in dropdown
    farmers = db.execute("SELECT id, username FROM users WHERE role = 'farmer'").fetchall()

    form = ReportForm()
    form.farmer_id.choices = [(f["id"], f["username"]) for f in farmers]

    if form.validate_on_submit():
        title = form.title.data
        report_type = form.report_type.data
        content = form.content.data
        farmer_id = form.farmer_id.data
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db.execute("""
            INSERT INTO reports (farmer_id, title, report_type, content, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (farmer_id, title, report_type, content, created_at))
        db.commit()

        flash("✅ Report submitted successfully", "success")
        return redirect(url_for("reports.add_report"))

    return render_template("add_report.html", form=form)



@reports_bp.route("/my_reports")
@login_required
def my_reports():
    if current_user.role != "farmer":
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    reports = db.execute("""
        SELECT title, report_type, content, created_at
        FROM reports
        WHERE farmer_id = ?
        ORDER BY created_at DESC
    """, (current_user.id,)).fetchall()

    return render_template("my_reports.html", reports=reports)


@reports_bp.route("/export_pdf")
@login_required
def export_pdf():
    if current_user.role != "farmer":
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    reports = db.execute("""
        SELECT title, report_type, content, created_at
        FROM reports
        WHERE farmer_id = ?
        ORDER BY created_at DESC
    """, (current_user.id,)).fetchall()

    # Create PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, f"Reports for {current_user.username}")
    y -= 40

    p.setFont("Helvetica", 10)
    for r in reports:
        if y < 100:  # new page if too low
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)

        p.drawString(50, y, f"Title: {r['title']}  ({r['report_type']}, {r['created_at']})")
        y -= 15
        text_lines = r['content'].split("\n")
        for line in text_lines:
            p.drawString(70, y, line)
            y -= 12
        y -= 15

    p.save()
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reports_{current_user.username}.pdf'
    return response
