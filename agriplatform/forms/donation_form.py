from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, NumberRange

class DonationForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    amount = DecimalField("Donation Amount ($)", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Donate Now")

