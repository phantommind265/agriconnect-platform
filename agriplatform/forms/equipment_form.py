from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class EquipmentForm(FlaskForm):
    name = StringField("Equipment Name", validators=[DataRequired()])
    type = StringField("Type", validators=[DataRequired()])
    model = StringField("Model")
    condition = SelectField("Condition", choices=[
        ('new', 'New'),
        ('good', 'Good'),
        ('needs repair', 'Needs Repair')
    ])
    location = StringField("Location")
    image = FileField("Upload Image", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField("Register Equipment")

