from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField
from wtforms.validators import DataRequired, Length

class TransportListingForm(FlaskForm):
    vehicle_type = StringField("Vehicle Type", validators=[DataRequired(), Length(max=50)])
    capacity = StringField("Capacity (e.g., 1 ton, 50 bags)", validators=[DataRequired(), Length(max=50)])
    route = StringField("Route (e.g., Lilongwe → Blantyre)", validators=[DataRequired(), Length(max=100)])
    available_date = DateField("Available Date", format='%Y-%m-%d', validators=[DataRequired()])
    price = StringField("Price (per trip or per bag)", validators=[DataRequired(), Length(max=50)])
    contact = StringField("Contact Info", validators=[DataRequired(), Length(max=50)])
    submit = SubmitField("Post Listing")

class BookTransportForm(FlaskForm):
    submit = SubmitField("Book")
