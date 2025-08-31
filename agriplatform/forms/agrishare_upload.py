from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class UploadFileForm(FlaskForm):
    file = FileField('Select file', validators=[
        DataRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt'], 'Invalid file type!')
    ])
    submit = SubmitField('Upload File')

