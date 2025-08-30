from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, DecimalField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class MarketItemForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    price = FloatField("Price (MWK)", validators=[DataRequired()])
    description = TextAreaField("Description")
    category = SelectField("Category", choices=[
        ("Fruits", "Fruits"),
        ("Vegetables", "Vegetables"),
        ("Livestock", "Livestock"),
        ("Grains", "Grains"),
        ("Legumes", "Legumes"),
        ("Inputs", "Inputs"),
        ("Tools", "Tools & Equipment"),
        ("Other", "Other")
    ], validators=[DataRequired()])
    seller_name = StringField("Your Name", validators=[DataRequired()])
    contact_info = StringField("Contact Info", validators=[DataRequired()])
    image = FileField("Item Image", validators=[FileAllowed(["jpg", "jpeg", "png"], "Images only!")])
    submit = SubmitField("Post Item")
