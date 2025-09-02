from flask import Blueprint, render_template, session, request
import json
from flask_login import login_required
from config import CROPS_DATA_PATH
from agriplatform.utils.translator import t

crop_bp = Blueprint("crop", __name__)

@crop_bp.route("/crops")
@login_required
def crop_list():
    with open(CROPS_DATA_PATH, "r", encoding="utf-8") as f:
        crops = json.load(f)
    
    query = request.args.get("q", "").lower()
    soil = request.args.get("soil", "")
    season = request.args.get("season", "")

    filtered = []
    for crop in crops:
        if query and query not in crop["name"].lower():
            continue
        if soil and soil not in crop["soil"].lower():
            continue
        if season and season not in crop["season"].lower():
            continue
        filtered.append(crop)

    return render_template("crops.html", crops=filtered, t=t)

@crop_bp.route("/crop/<name>")
@login_required
def crop_detail(name):
    with open(CROPS_DATA_PATH, "r", encoding="utf-8") as f:
        crops = json.load(f)
    crop = next((c for c in crops if c["name"].lower() == name.lower()), None)
    if not crop:
        return (f"No crop data").format(name), 404
    return render_template("crop_detail.html", crop=crop, t=t)
