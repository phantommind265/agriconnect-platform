import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user
from agriplatform.forms.data_form import DataSubmissionForm
import os
import csv
import io
from flask import Response
from openpyxl import Workbook

data_bp = Blueprint("data_submission", __name__, url_prefix="/data")
DB_PATH = os.path.join("agriplatform", "agriconnect.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@data_bp.teardown_app_request
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@data_bp.route("/submit", methods=["GET", "POST"])
@login_required
def submit_data():
    # Only farmers & extension workers
    if current_user.role not in ["farmer", "extension_worker"]:
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    form = DataSubmissionForm()
    if form.validate_on_submit():
        db = get_db()
        db.execute("""
            INSERT INTO data_submissions (farmer_id, crop, season, yield_amount, inputs_used, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            current_user.id,
            form.crop.data,
            form.season.data,
            form.yield_amount.data,
            form.inputs_used.data,
            form.notes.data,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        db.commit()
        flash("✅ Data submitted successfully", "success")
        return redirect(url_for("data_submission.my_submissions"))

    return render_template("submit_data.html", form=form)



@data_bp.route("/my_submissions")
@login_required
def my_submissions():
    if current_user.role != "farmer":
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    submissions = db.execute("""
        SELECT crop, season, yield_amount, inputs_used, notes, created_at
        FROM data_submissions
        WHERE farmer_id = ?
        ORDER BY created_at DESC
    """, (current_user.id,)).fetchall()

    return render_template("my_submissions.html", submissions=submissions)


@data_bp.route("/all_submissions", methods=["GET"])
@login_required
def all_submissions():
    if current_user.role not in ["admin", "extension_worker"]:
        flash("Unauthorized access", "danger")
        return redirect(url_for("auth.login"))

    db = get_db()
    submissions = db.execute("""
        SELECT ds.crop, ds.season, ds.yield_amount, ds.inputs_used, ds.notes, ds.created_at,
               u.username AS farmer_name
        FROM data_submissions ds
        JOIN users u ON ds.farmer_id = u.id
        ORDER BY ds.created_at DESC
    """).fetchall()

    # --- CSV Export ---
    if "export" in dict(request.args):
        export_type = request.args.get("export")

        if export_type == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Farmer", "Crop", "Season", "Yield", "Inputs", "Notes", "Date"])
            for s in submissions:
                writer.writerow([s["farmer_name"], s["crop"], s["season"], s["yield_amount"],
                                 s["inputs_used"], s["notes"], s["created_at"]])
            output.seek(0)
            return Response(output, mimetype="text/csv",
                            headers={"Content-Disposition": "attachment;filename=submissions.csv"})

        elif export_type == "xlsx":
            wb = Workbook()
            ws = wb.active
            ws.title = "Submissions"
            ws.append(["Farmer", "Crop", "Season", "Yield", "Inputs", "Notes", "Date"])
            for s in submissions:
                ws.append([s["farmer_name"], s["crop"], s["season"], s["yield_amount"],
                           s["inputs_used"], s["notes"], s["created_at"]])

            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            return Response(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            headers={"Content-Disposition": "attachment;filename=submissions.xlsx"})

    return render_template("all_submissions.html", submissions=submissions)


