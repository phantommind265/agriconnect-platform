from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

class SoilUploadForm(FlaskForm):
    soil_image = FileField(
        'Upload a clear photo of your soil',
        validators=[
            FileRequired(message='Please upload a soil image'),
            FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG and PNG images are allowed')
        ]
    )
    submit = SubmitField('Analyze Soil')

