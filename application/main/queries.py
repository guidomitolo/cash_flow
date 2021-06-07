from datetime import datetime

from application import db
from application import current_app as app
from application.main.models import Balance, Credit, CreditCard, CreditStatement

from flask_login import current_user
# db orm func
from sqlalchemy import or_



def get_credit(page=None, card_number=None, due_date=None, type=None):

    if due_date:
        statement_id = CreditStatement.query.filter_by(due_date = due_date).first().id

    if card_number and due_date:
        return Credit.query\
                .filter(
                        Credit.user_id == current_user.id,
                        Credit.statement == statement_id,
                        Credit.card_number == card_number
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    elif card_number:
        return Credit.query\
            .filter(
                    Credit.user_id == current_user.id,
                    Credit.card_number == card_number,
            )\
            .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    elif due_date:
        return Credit.query\
            .filter(
                    Credit.user_id == current_user.id,
                    Credit.statement == statement_id,
            )\
            .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    elif type:
        return Credit.query\
            .filter(
                    Credit.user_id == current_user.id,
                    Credit.type == type,
            )\
            .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])    
    else:
        return Credit.query\
                .filter(
                    Credit.user_id == current_user.id,
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])


def get_data(bank=None, page=None, start=None, end=None, tag=None):

    if start and end:
        return Balance.query\
                .filter(
                        Balance.user_id == current_user.id,
                        Balance.bank == bank,
                        Balance.timestamp >= datetime.strptime(start, "%Y-%m-%d"),
                        Balance.timestamp <= datetime.strptime(end, "%Y-%m-%d"),
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    elif start:
        return Balance.query\
            .filter(
                    Balance.user_id == current_user.id,
                    Balance.bank == bank,
                    Balance.timestamp >= datetime.strptime(start, "%Y-%m-%d")
            )\
            .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    elif tag:
        return Balance.query\
            .filter(
                    Balance.user_id == current_user.id,
                    Balance.type == tag,
            )\
            .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])    
    elif bank:
        return Balance.query\
                .filter(
                    Balance.user_id == current_user.id,
                    Balance.bank == bank
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    else:
        return Balance.query\
                .filter(
                    Balance.user_id == current_user.id,
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])


def get_dates(bank, start=None, credit=None):

    if credit:
        if bank and start:
            return Credit.query.with_entities(Credit.timestamp) \
                .filter(Credit.bank == bank, Credit.timestamp >= datetime.strptime(start, "%Y-%m-%d")) \
                .order_by(Credit.timestamp) \
                .distinct().all()
        else:
            return Credit.query.with_entities(Credit.timestamp) \
                .filter(Credit.bank == bank) \
                .order_by(Credit.timestamp) \
                .distinct().all()
    else:
        if bank and start:
            return Balance.query.with_entities(Balance.timestamp) \
                .filter(Balance.bank == bank, Balance.timestamp >= datetime.strptime(start, "%Y-%m-%d")) \
                .order_by(Balance.timestamp) \
                .distinct().all()
        else:
            return Balance.query.with_entities(Balance.timestamp) \
                .filter(Balance.bank == bank) \
                .order_by(Balance.timestamp) \
                .distinct().all()


def add_credit_card():

    cards = CreditCard.query.all()
    credit = Credit.query.all()
    for card in cards:
        get_code = int(str(card.number)[-4:])
        for transaction in credit:
            if transaction.card_number is None:
                if get_code == transaction.card_code:
                    transaction.card_number = card.number
    db.session.commit()


def classification():

    esparcimiento = Credit.query.filter(
            or_(
                Credit.transaction.like("%KANSAS%"),
                Credit.transaction.like("%HOTEL%"),
            )
        ).all()
    for row in esparcimiento:
        if row.type is None:
            row.type = 'Esparcimiento'
            db.session.commit()

    digital = Credit.query.filter(
        or_(
            Credit.transaction.like("%spotify%"),
            Credit.transaction.like("%NETFLIX%"),
            Credit.transaction.like("%Amazon%"),
        )
    ).all()
    for row in digital:
        if row.type is None:
            row.type = 'Digital'
            db.session.commit()

    combustible = Credit.query.filter(
        or_(
            Credit.transaction.like("%SHELL%"),
            Credit.transaction.like("%YPF%"),
        )
    ).all()
    for row in combustible:
        if row.type is None:
            row.type = 'Combustible'
            db.session.commit()

    movilidad = Credit.query.filter(
        or_(
            Credit.transaction.like("%AUBASA%"),
            Credit.transaction.like("%AUTOP%"),
        )
    ).all()
    for row in movilidad:
        if row.type is None:
            row.type = 'Movilidad'
            db.session.commit()

    alimentacion = Credit.query.filter(
        or_(
            Credit.transaction.like("%CARNICER%"),
            Credit.transaction.like("%COTO%"),
            Credit.transaction.like("%ALMACEN%"),
            Credit.transaction.like("%FIAMBRE%"),
            Credit.transaction.like("%JUMBO%"),
        )
    ).all()
    for row in alimentacion:
        if row.type is None:
            row.type = 'Alimentacion'
            db.session.commit()

    indumentaria = Credit.query.filter(
        or_(
            Credit.transaction.like("%CARDON%"),
            Credit.transaction.like("%DEXTER%"),
            Credit.transaction.like("%LAZARO%"),
            Credit.transaction.like("%DAFITI%"),

        )
    ).all()
    for row in indumentaria:
        if row.type is None:
            row.type = 'Indumentaria'
            db.session.commit()

    mascota = Credit.query.filter(
        or_(
            Credit.transaction.like("%PUPIS%"),
        )
    ).all()
    for row in mascota:
        if row.type is None:
            row.type = 'Mascota'
            db.session.commit()


def tag_due_dates():

    dues = Balance.query.filter(
            or_(
                Balance.detail.like("%CUENTA VISA%"), 
                Balance.detail.like("%CUENTA MASTERCARD%")
            )
        ).all()
    for row in dues:
        if row.type is None:
            row.type = 'Vencimiento Tarjeta'
            db.session.commit()

    impuestos = Balance.query.filter(
        or_(
            Balance.detail.like("%IVA%"),
            Balance.detail.like("%LEY%"),
            Balance.detail.like("%IMPUESTO%"),
        )
    ).all()
    for row in impuestos:
        if row.type is None:
            row.type = 'Impuestos'
            db.session.commit()


def balance_card_payments():

    balance_payments = Balance.query.filter_by(type="Vencimiento Tarjeta").all()
    credit_statement = CreditStatement.query.all()
    
    for payment in balance_payments:
        if payment.id_statement is None:
            for due_date in credit_statement:
                if payment.timestamp == due_date.due_date:
                    payment.id_statement = due_date.id

    db.session.commit()