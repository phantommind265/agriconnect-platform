from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

class MaintenanceForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()], format='%Y-%m-%d')
    cost = DecimalField("Cost", validators=[Optional()])
    submit = SubmitField("Add Maintenance")

