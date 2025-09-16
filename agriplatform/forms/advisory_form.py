from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class AdvisoryForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    crop = StringField("Crop (Optional)", validators=[Optional()])
    district = StringField("District (Optional)", validators=[Optional()])
    submit = SubmitField("Post Advisory")
