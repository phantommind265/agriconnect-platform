from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Optional

class ExpressInterestForm(FlaskForm):
    message = TextAreaField("Message to Buyer (optional)", validators=[Optional()])
    submit = SubmitField("Send Interest")
