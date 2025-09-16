from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class MarketLinkageForm(FlaskForm):
    crop = StringField("Crop", validators=[DataRequired()])
    buyer_name = StringField("Buyer/Company Name", validators=[DataRequired()])
    price_range = StringField("Price Range (optional)", validators=[Optional()])
    location = StringField("Location (optional)", validators=[Optional()])
    contact_info = StringField("Contact Info (optional)", validators=[Optional()])
    notes = TextAreaField("Additional Notes", validators=[Optional()])
    submit = SubmitField("Add Market Linkage")


