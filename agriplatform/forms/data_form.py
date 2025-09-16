from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional

class DataSubmissionForm(FlaskForm):
    crop = StringField("Crop", validators=[DataRequired()])
    season = SelectField("Season", choices=[
        ("2024/25", "2024/25"),
        ("2023/24", "2023/24"),
        ("2022/23", "2022/23"),
        ("2021/22", "2021/22"),
        ("2020/21", "2020/21")
    ], validators=[DataRequired()])
    yield_amount = FloatField("Yield (Kg or Tons)", validators=[Optional()])
    inputs_used = TextAreaField("Inputs Used (fertilizers, seeds, chemicals)", validators=[Optional()])
    notes = TextAreaField("Additional Notes", validators=[Optional()])
    submit = SubmitField("Submit Data")


