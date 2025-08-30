from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class JoinSessionForm(FlaskForm):
    session_value = StringField('Paste Session URL or ID', validators=[DataRequired()])
    submit = SubmitField('Join')

