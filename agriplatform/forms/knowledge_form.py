from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired

class KnowledgeResourceForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    category = SelectField("Category", choices=[
        ("crop_management", "Crop Management"),
        ("livestock", "Livestock"),
        ("market", "Market"),
        ("technology", "Technology"),
        ("climate", "Climate & Weather"),
        ("other", "Other")
    ])
    file = FileField("Upload File (Optional)")
    submit = SubmitField("Add Resource")


