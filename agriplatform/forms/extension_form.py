from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Optional

class FarmerSearchForm(FlaskForm):
    username = StringField('Username', validators=[Optional()])
    district = StringField('District', validators=[Optional()])
    status = SelectField(
        'Status',
        choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')],
        validators=[Optional()]
    )
    submit = SubmitField('Search')

