from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, Form, StringField, IntegerField
from wtforms.validators import Optional


from wtforms.fields.html5 import DateField


class FileSubmit(FlaskForm):
    file = FileField('Archivo', validators=[FileAllowed(['xlsx'], 'Sólo xlsx'), FileRequired()])
    upload = SubmitField('Subir')

class TagForm(Form):
    tag = StringField(validators=[Optional()])