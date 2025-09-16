from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class NotificationForm(FlaskForm):
    #title = StringField("Title", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    link = StringField("Optional Link", validators=[Optional()])
    target = SelectField(
        "Send To",
        choices=[
            ("all", "All Users"),
            ("farmers", "Farmers Only"),
            ("extension", "Extension Workers Only"),
            ("admin", "Admins Only"),
            ("user", "Specific User (enter ID below)")
        ],
        validators=[DataRequired()]
    )
    user_id = StringField("Specific User ID (only if chosen above)", validators=[Optional()])
    submit = SubmitField("Send Notification")


