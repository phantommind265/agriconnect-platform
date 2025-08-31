from flask_wtf import FlaskForm
from wtforms import SubmitField

class CreateShareSessionForm(FlaskForm):
    close_session = SubmitField("Close Session")

