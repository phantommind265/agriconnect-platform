from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional

class ServiceForm(FlaskForm):
    name = StringField("Service Name", validators=[DataRequired()])
    service_type = SelectField(
        "Service Type",
        choices=[
            ("Agro-dealer", "Agro-dealer"),
            ("Veterinary", "Veterinary"),
            ("Market", "Market"),
            ("Extension Officer", "Extension Officer"),
        ],
        validators=[DataRequired()]
    )
    district = StringField("District", validators=[DataRequired()])
    contact = StringField("Contact Info (Optional)", validators=[Optional()])
    submit = SubmitField("Add Service")


