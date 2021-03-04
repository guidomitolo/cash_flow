from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, Form, StringField, SelectField, FieldList, FormField
from wtforms.validators import Optional

class FileSubmit(FlaskForm):
    file = FileField('Archivo', validators=[FileAllowed(['xlsx'], 'Sólo xlsx'), FileRequired()])
    upload = SubmitField('Subir')

class TagForm(Form):
    tag = StringField(validators=[Optional()])