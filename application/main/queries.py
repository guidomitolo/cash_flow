from datetime import datetime

from application import db
from application import current_app as app
from application.main.models import Balance, Credit, CreditCard, CreditPayments

from flask_login import current_user
# db orm func
from sqlalchemy import or_


def get_data(bank=None, page=None, start=None, end=None, tag=None, credit=None):

    if credit:
        if start and end:
            return Credit.query\
                    .filter(
                            Credit.user_id == current_user.id,
                            Credit.bank == bank,
                            Credit.timestamp >= datetime.strptime(start, "%Y-%m-%d"),
                            Credit.timestamp <= datetime.strptime(end, "%Y-%m-%d"),
                    )\
                    .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
        elif start:
            return Credit.query\
                .filter(
                        Credit.user_id == current_user.id,
                        Credit.bank == bank,
                        Credit.timestamp >= datetime.strptime(start, "%Y-%m-%d")
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
        elif tag:
            return Credit.query\
                .filter(
                        Credit.user_id == current_user.id,
                        Credit.tag == tag,
                )\
                .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])    
        elif bank:
            return Credit.query\
                    .filter(
                        Credit.user_id == current_user.id,
                        Credit.bank == bank
                    )\
                    .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
        else:
            return Credit.query\
                    .filter(
                        Credit.user_id == current_user.id,
                    )\
                    .paginate(page=page, per_page=app.config['ROWS_PER_PAGE'])
    else:
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
                        Balance.tag == tag,
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


def classification():

    esparcimiento = Credit.query.filter(
            or_(
                Credit.creditor.like("%KANSAS%"),
                Credit.creditor.like("%HOTEL%"),
            )
        ).all()
    for row in esparcimiento:
        if row.tag is None:
            row.tag = 'Esparcimiento'
            db.session.commit()

    digital = Credit.query.filter(
        or_(
            Credit.creditor.like("%spotify%"),
            Credit.creditor.like("%NETFLIX%"),
            Credit.creditor.like("%Amazon%"),
        )
    ).all()
    for row in digital:
        if row.tag is None:
            row.tag = 'Digital'
            db.session.commit()

    combustible = Credit.query.filter(
        or_(
            Credit.creditor.like("%SHELL%"),
            Credit.creditor.like("%YPF%"),
        )
    ).all()
    for row in combustible:
        if row.tag is None:
            row.tag = 'Combustible'
            db.session.commit()

    movilidad = Credit.query.filter(
        or_(
            Credit.creditor.like("%AUBASA%"),
            Credit.creditor.like("%AUTOP%"),
        )
    ).all()
    for row in movilidad:
        if row.tag is None:
            row.tag = 'Movilidad'
            db.session.commit()

    alimentacion = Credit.query.filter(
        or_(
            Credit.creditor.like("%CARNICER%"),
            Credit.creditor.like("%COTO%"),
            Credit.creditor.like("%ALMACEN%"),
            Credit.creditor.like("%FIAMBRE%"),
            Credit.creditor.like("%JUMBO%"),
        )
    ).all()
    for row in alimentacion:
        if row.tag is None:
            row.tag = 'Alimentacion'
            db.session.commit()

    impuestos = Credit.query.filter(
        or_(
            Credit.creditor.like("%IVA%"),
            Credit.creditor.like("%LEY%"),
            Credit.creditor.like("%IMPUESTO%"),
        )
    ).all()
    for row in impuestos:
        print(impuestos)
        if row.tag is None:
            row.tag = 'Impuestos'
            db.session.commit()

    indumentaria = Credit.query.filter(
        or_(
            Credit.creditor.like("%CARDON%"),
            Credit.creditor.like("%DEXTER%"),
            Credit.creditor.like("%LAZARO%"),
            Credit.creditor.like("%DAFITI%"),

        )
    ).all()
    for row in indumentaria:
        if row.tag is None:
            row.tag = 'Indumentaria'
            db.session.commit()

    mascota = Credit.query.filter(
        or_(
            Credit.creditor.like("%PUPIS%"),
        )
    ).all()
    for row in mascota:
        if row.tag is None:
            row.tag = 'Mascota'
            db.session.commit()


def tag_due_dates():

    dues = Balance.query.filter(
            or_(
                Balance.detail.like("%CUENTA VISA%"), 
                Balance.detail.like("%CUENTA MASTERCARD%")
            )
        ).all()
    for row in dues:
        if row.tag is None:
            row.tag = 'Vencimiento Tarjeta'
            db.session.commit()

    impuestos = Balance.query.filter(
        or_(
            Balance.detail.like("%IVA%"),
            Balance.detail.like("%LEY%"),
            Balance.detail.like("%IMPUESTO%"),
        )
    ).all()
    for row in impuestos:
        if row.tag is None:
            row.tag = 'Impuestos'
            db.session.commit()

def populate_payments(dues):

    cards = CreditCard.query.all()

    for row in dues:
        for card in cards:
            if card.card in row.detail:
                if CreditPayments.query.filter(
                    CreditPayments.due_date == row.timestamp,
                    CreditPayments.card_payment == row.id
                    ).first():
                    pass
                else:
                    pagos = CreditPayments(
                        user_id = current_user.id,
                        card_number = card.card_number,
                        due_date = row.timestamp.date(),
                        card_payment = row.id,
                    )
                    db.session.add(pagos)
                    db.session.commit()