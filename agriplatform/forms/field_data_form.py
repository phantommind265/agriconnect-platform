from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional

class FieldDataForm(FlaskForm):
    farmer_id = IntegerField('Farmer ID (optional)', validators=[Optional()])
    district = StringField('District', validators=[DataRequired()])
    crop = StringField('Crop', validators=[DataRequired()])
    observation = TextAreaField('Observation', validators=[DataRequired()])
    submit = SubmitField('Submit Data')


