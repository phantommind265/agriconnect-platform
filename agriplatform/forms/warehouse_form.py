from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional, Length

class WarehouseListingForm(FlaskForm):
    location = StringField("Location", validators=[DataRequired(), Length(max=200)])
    capacity = StringField("Capacity (e.g. 50 bags, 2 tons)", validators=[DataRequired(), Length(max=100)])
    price_per_day = FloatField("Price per day (MWK)", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Optional(), Length(max=800)])
    submit = SubmitField("Add Warehouse")

class BookWarehouseForm(FlaskForm):
    booked_from = DateField("From (YYYY-MM-DD)", format='%Y-%m-%d', validators=[DataRequired()])
    booked_to = DateField("To (YYYY-MM-DD)", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Book")

class StatusForm(FlaskForm):
    submit = SubmitField("Submit")
