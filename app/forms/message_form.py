from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField #, SelectField, HiddenField
from wtforms.validators import DataRequired

class MessageForm(FlaskForm):
    #receiver_id = SelectField("Receiver", coerce=int, validators=[DataRequired()])
    content = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")

