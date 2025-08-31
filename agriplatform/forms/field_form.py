from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange

class FieldForm(FlaskForm):
    name = StringField("Field Name", validators=[DataRequired(), Length(min=2, max=150)])
    size = FloatField("Field Size (acres)", validators=[DataRequired(), NumberRange(min=0.1)])
    location = StringField("Location", validators=[Length(max=200)])
    submit = SubmitField("Save Field")



class CropForm(FlaskForm):
    name = StringField("Crop Name", validators=[DataRequired()])
    season = SelectField("Season", choices=[("Rainy", "Rainy"), ("Dry", "Dry"), ("Winter", "Winter")])
    expected_yield = FloatField("Expected Yield (tonnes/acre)", validators=[NumberRange(min=0)])
    field_id = SelectField("Field", coerce=int)  # dropdown of fields
    submit = SubmitField("Save Crop")

