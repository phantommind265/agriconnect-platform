from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ProfitEstimateForm(FlaskForm):
    crop = SelectField("Crop", validators=[DataRequired()])
    area = FloatField("Area (acres)", validators=[DataRequired()])
    cost = FloatField("Cost (MWK)", validators=[DataRequired()])
    yield_per_acre = FloatField("Yield per acre (tons)", validators=[DataRequired()])
    month = StringField("Month", validators=[DataRequired()])
    submit = SubmitField("Estimate Profit")


