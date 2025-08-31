import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from agriplatform.forms.soil_form import SoilUploadForm
import random
import uuid
from flask import current_app
#from app.routes.soil_data.soil_inference import analyze_soil

soil_bp = Blueprint('soil', __name__)

"""
@soil_bp.route('/soil_analyzer', methods=['GET', 'POST'])
def soil_analyzer():
    form = SoilUploadForm()

    if form.validate_on_submit():
        file = form.soil_image.data

        # Make filename safe
        filename = secure_filename(file.filename)
        file_path = os.path.join('static/uploads', filename)

        # Save file
        file.save(file_path)

        # Redirect to results page (we’ll build it in Step 5)
        flash("Image uploaded successfully!", "success")
        return redirect(url_for('soil.soil_results', filename=filename))

    return render_template('soil_analyzer.html', form=form)
"""

@soil_bp.route('/soil_analyzer', methods=['GET', 'POST'])
def soil_analyzer():
    form = SoilUploadForm()

    if form.validate_on_submit():
        file = form.soil_image.data

        # Create unique filename to avoid overwriting
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"

        # Full path to save file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

        # Ensure upload folder exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save file
        file.save(file_path)

        flash("Image uploaded successfully!", "success")
        return redirect(url_for('soil.soil_results', filename=filename))

    return render_template('soil_analyzer.html', form=form)
"""
@soil_bp.route('/soil_results/<filename>')
def soil_results(filename):
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        pred_label, probs = analyze_soil(file_path)
    except Exception as e:
        flash("Error analyzing image: " + str(e), "danger")
        return redirect(url_for('soil.soil_analyzer'))

    # suggestions same as before (map pred_label to suggestions)
    suggestions = {...}  # keep your mapping
    crops = suggestions[pred_label]["crops"]
    tip = suggestions[pred_label]["tip"]

    return render_template('soil_results.html',
                           filename=filename,
                           soil_type=pred_label,
                           crops=crops,
                           tip=tip,
                           confidences=probs)
"""

@soil_bp.route('/soil_results/<filename>')
def soil_results(filename):
    # Temporary fake classification
    soil_types = ["Sandy", "Clay", "Loamy"]
    detected_soil = random.choice(soil_types)

    # Suggestions based on type
    suggestions = {
        "Sandy": {
            "crops": ["Cassava", "Groundnuts", "Sweet Potatoes"],
            "tip": "Add compost to improve water retention."
        },
        "Clay": {
            "crops": ["Rice", "Sugarcane", "Soybeans"],
            "tip": "Ensure proper drainage to avoid waterlogging."
        },
        "Loamy": {
            "crops": ["Maize", "Tomatoes", "Beans"],
            "tip": "Maintain organic matter for optimal fertility."
        }
    }

    return render_template(
        'soil_results.html',
        filename=filename,
        soil_type=detected_soil,
        crops=suggestions[detected_soil]["crops"],
        tip=suggestions[detected_soil]["tip"]
    )

