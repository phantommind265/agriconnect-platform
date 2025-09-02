from flask import Blueprint, render_template, request
import json
from flask_login import login_required
from config import PESTS_DATA_PATH
from agriplatform.utils.translator import t

pest_bp = Blueprint('pest', __name__, url_prefix='/pests')

def load_pests():
    with open(PESTS_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

@pest_bp.route('/')
def list_pests():
    #pests = load_pests()
    #return render_template('pest/pests.html', pests=pests, t=t)
    query = request.args.get('q', '').strip().lower()
    pests = load_pests()

    if query:
        pests = [
                p for p in pests
                if query in p["name"].lower() or query in p["symptoms"].lower()
                ]
    return render_template(
        'pest/pests.html',
        pests=pests,
        query=query,
        t=t
    )

@pest_bp.route('/<crop_name>')
@login_required
def pests_by_crop(crop_name):
    pests = load_pests()
    crop_pests = [
            p for p in pests
            if crop_name.lower() in [c.lower() for c in p.get("crops", [])]
            ]
    return render_template(
            'pest/pests_by_crop.html',
            crop=crop_name.capitalize(),
            pests=crop_pests,
            t=t
            )

@pest_bp.route('/view/<name>')
def view_pest(name):
    pests = load_pests()
    pest = next((p for p in pests if p["name"].lower() == name.lower()), None)

    if not pest:
        return render_template("404.html", message=t("no_pests_found"))
    return render_template("pest/pest_detail.html", pest=pest, t=t)





