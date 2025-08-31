from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import Optional
from flask_wtf.file import FileAllowed

class EditProfileForm(FlaskForm):
    profile_pic = FileField("Update Profile Picture", validators=[
        Optional(),
        FileAllowed(["jpg", "jpeg", "png"], "Images only!")
    ])
    submit = SubmitField("Save Changes")


