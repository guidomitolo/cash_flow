from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, Form, StringField, IntegerField, validators
from wtforms.validators import Optional, DataRequired, ValidationError
from wtforms.fields.html5 import DateField

from application.main.models import CreditCard

from wtforms import FieldList, FormField
from flask_wtf import FlaskForm


class FileSubmitBalance(FlaskForm):
    file = FileField('Archivo', validators=[FileAllowed(['xlsx'], 'Sólo XLSX'), FileRequired()])
    upload = SubmitField('Subir')


class FileSubmitCredit(FlaskForm):
    file = FileField('Archivo', validators=[FileAllowed(['pdf'], 'Sólo PDF'), FileRequired()])
    upload = SubmitField('Subir')


class TagForm(Form):
    tag = StringField(validators=[Optional()])


class LoadCreditCard(FlaskForm):
    card = StringField('Tarjeta', validators=[DataRequired()])
    bank = StringField('Banco', validators=[DataRequired()])
    card_number = IntegerField('Número', validators=[DataRequired(message="Completar Campo"), validators.NumberRange(min=0, max=100000000, message="Número Incorrecto")])
    expiration = DateField('Vencimiento', validators=[DataRequired()])

    # password control in forms, not in routes/views
    def validate_card(self, card_number):
        card = CreditCard.query.filter_by(number = card_number.data).first()
        if card is not None:
            raise ValidationError('Tarjeta existente')


def tags_creator(rows):

    class TagsList(FlaskForm):
        tags = FieldList(FormField(TagForm), min_entries=rows)

    return TagsList()