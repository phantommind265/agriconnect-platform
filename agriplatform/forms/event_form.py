from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, TimeField, FileField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileAllowed

class EventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional()])
    location = StringField("Location", validators=[DataRequired()])
    date = DateField("Date", validators=[DataRequired()], format='%Y-%m-%d')
    time = TimeField("Time", validators=[DataRequired()], format='%H:%M')
    organizer = StringField("Organizer", validators=[Optional()])
    flyer = FileField("Flyer Image", validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField("Save Event")



