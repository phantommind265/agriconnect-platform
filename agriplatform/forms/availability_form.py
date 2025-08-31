from wtforms import DateField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import SubmitField

class AvailabilityForm(FlaskForm):
    date = DateField("Select Date", validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField("Mark as Unavailable")

