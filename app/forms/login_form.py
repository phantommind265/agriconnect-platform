from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Login")
