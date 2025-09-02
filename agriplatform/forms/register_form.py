from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, EqualTo, Length, Email

class RegisterForm(FlaskForm):
    profile_pic = FileField("Profile Picture")
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    role = SelectField("Role", choices=[
        ("farmer", "Farmer"),
        ("extension_worker", "Extension Worker"),
        #("admin", "Admin")
        ], validators=[DataRequired()])
    language = SelectField("Language", choices=[("en", "English"), ("ny", "Chichewa")], validators=[DataRequired()])
    submit = SubmitField("Register")



class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")



class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField("Reset Password")
