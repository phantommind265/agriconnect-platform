from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed

class ProfileForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    farm_location = StringField("Farm Location", validators=[Optional()])
    contact_info = StringField("Contact Info", validators=[Optional()])
    crops = StringField("Crops", validators=[Optional()])
    animals = StringField("Animals", validators=[Optional()])
    bio = TextAreaField("Bio", validators=[Optional()])

    image = FileField("Profile Picture", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only')])

    submit = SubmitField("Save")

