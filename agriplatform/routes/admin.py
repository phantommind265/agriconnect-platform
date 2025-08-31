from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from agriplatform.routes.auth_routes import admin_required
from agriplatform.utils.translator import t
from agriplatform.utils.storage import load_json, save_json
import json
import os
from flask import current_app

PESTS_PATH = os.path.join("agriplatform", "data", "pests.json")
CROPS_PATH = os.path.join("agriplatform", "data", "crops.json")
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", t=t)

@admin_bp.route('/crops')
@admin_required
def manage_crops():
    with open(CROPS_PATH, "r", encoding="utf-8") as f:
        crops = json.load(f)
    return render_template("admin/manage_crops.html", crops=crops, t=t)

@admin_bp.route("/crops/delete/<crop_name>", methods=["POST"])
@admin_required
def delete_crop(crop_name):
    with open(CROPS_PATH, "r", encoding="utf-8") as f:
        crops = json.load(f)

    updated_crops = [c for c in crops if c["name"].lower() != crop_name.lower()]
    with open(CROPS_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_crops, f, indent=2)

    flash(t("crop_deleted"), "success")
    return redirect(url_for("admin.manage_crops"))

@admin_bp.route('/pests')
@admin_required
def manage_pests():
    with open(PESTS_PATH, "r", encoding="utf-8") as f:
        pests = json.load(f)
    return render_template("admin/manage_pests.html", pests=pests, t=t)

@admin_bp.route("/pests/delete/<pest_name>", methods=["POST"])
@admin_required
def delete_pest(pest_name):
    with open(PESTS_PATH, "r", encoding="utf-8") as f:
        pests = json.load(f)

    updated_pests = [p for p in pests if p["name"].lower() != pest_name.lower()]
    with open(PESTS_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_pests, f, indent=2)

    flash(t("pest_deleted"), "success")
    return render_template("admin/manage_pests.html")

@admin_bp.route("/crops/add", methods=["GET", "POST"])
@admin_required
def add_crop():
    if request.method == "POST":
        new_crop = {
                "name": request.form["name"],
                "description": request.form["description"],
                "growth_cycle": request.form["growth_cycle"],
                "soil_type": request.form["soil_type"],
                "season": request.form["season"]
        }
        #with open(CROPS_PATH, "r", encoding="utf-8") as f:
         #   crops = json.load(f)

        crops = load_json(CROPS_PATH)

        crops.append(new_crop)

        #with open(CROPS_PATH, "w", encoding="utf-8") as f:
         #   json.dump(crops, f, indent=2)
        save_json(CROPS_PATH, crops)

        flash(t("crop_added"), "success")
        return redirect(url_for("admin.manage_crops"))
    return render_template("admin/crop_form.html", crop=None, t=t)

@admin_bp.route("/crops/edit/<crop_name>", methods=["GET", "POST"])
@admin_required
def edit_crop(crop_name):
    with open(CROPS_PATH, "r", encoding="utf-8") as f:
        crops = json.load(f)

    crop = next(( c for c in crops if c["name"].lower() == crop_name.lower()), None)
    if not crop:
        flash(t("crop_not_found"), "error")
        return redirect(url_for("admin.manage_crops"))

    if request.method == "POST":
        crop.update({
            "name": request.form["name"],
            "description": request.form["description"],
            "growth_cycle": request.form["growth_cycle"],
            "soil_type": request.form["soil_type"],
            "season": request.form["season"]
            })

        with open(CROPS_PATH, "w", encoding="utf-8") as f:
            json.dump(crops, f, indent=2)

        flash(t("crop_updated"), "success")
        return redirect(url_for("admin.manage_crops"))
    return render_template("admin/crop_from.html", crop=crop, t=t)

@admin_bp.route("/pests/add", methods=["GET", "POST"])
@admin_required
def add_pest():
    if request.method == "POST":
        new_pest = {
                "name": request.form["name"],
                "symptoms": request.form["symptoms"],
                "solution": request.form["solution"],
                "crops": [c.strip() for c in request.form["crops"].split(",")]
                }
        with open(PESTS_PATH, "r", encoding="utf-8") as f:
            pests = json.load(f)

        pests.append(new_pest)

        with open(PESTS_PATH, "w", encoding="utf-8") as f:
            json.dump(pests, f, indent=2)

        flash(t("pest_added"), "success")
        return redirect(url_for("admin.manage_pests"))
    return render_template("admin/pest_form.html", pest=None, t=t)

@admin_bp.route("/pests/edit/<pest_name>", methods=["GET", "POST"])
@admin_required
def edit_pest(pest_name):
    with open(PESTS_PATH, "r", encoding="utf-8") as f:
        pests = json.load(f)

    pest = next((p for p in pests if p["name"].lower() == pest_name.lower()), None)
    if not pest:
        flash(t("pest_not_found"), "error")
        return redirect(url_for("admin.manage_pests"))

    if request.method == "POST":
        pest.update({
            "name": request.form["name"],
            "symptoms": request.form["symptoms"],
            "solution": request.form["solution"],
            "crops": [c.strip() for c in request.form["crops"].split(",")]
                })
        with open(PESTS_PATH, "w", encoding="utf-8") as f:
            json.dump(pests, f, indent=2)

        flash(t("pest_updated"), "success")
        return redirect(url_for("admin.manage_pests"))
    return render_template("admin/pest_form.html", pest=pest, t=t)

