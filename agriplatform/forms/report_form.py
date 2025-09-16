from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ReportForm(FlaskForm):
    title = StringField("Report Title", validators=[DataRequired()])
    report_type = SelectField("Report Type", choices=[
        ("yield", "Yield Report"),
        ("profit", "Profit Report"),
        ("market", "Market Report"),
        ("general", "General Report")
    ], validators=[DataRequired()])
    content = TextAreaField("Report Content", validators=[DataRequired()])
    farmer_id = SelectField("Farmer", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Submit Report")


