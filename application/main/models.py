from application import db

class Balance(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bank = db.Column(db.String(64))
    account_n = db.Column(db.String(120), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    detail = db.Column(db.String(128))  
    flow = db.Column(db.Integer)
    bal = db.Column(db.Integer)
    tag = db.Column(db.String(128), index=True)
    # relationship with balance card payment
    card_payment = db.relationship('CreditPayments', backref='card_payed', lazy='dynamic')

    def __repr__(self):
        return '<Account nro. {}>'.format(self.account_n)


class CreditCard(db.Model):
    __tablename__ = 'creditcard'
    # populates two other tables
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_number = db.Column(db.Integer, index=True, primary_key=True)
    card = db.Column(db.String(64))
    expiration = db.Column(db.DateTime)

    credit = db.relationship('Credit', backref='transactions', lazy='dynamic')
    payments = db.relationship('CreditPayments', backref='payments', lazy='dynamic')

    def __repr__(self):
        return '<Card {0} {1}>'.format(self.card, self.card_number)


class Credit(db.Model):
    __tablename__ = 'credit'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    card_summary = db.Column(db.DateTime, index=True)
    
    bank = db.Column(db.String(64))
    card_number = db.Column(db.Integer, db.ForeignKey('creditcard.card_number'))
    timestamp = db.Column(db.DateTime, index=True)
    creditor = db.Column(db.String(128))  
    share = db.Column(db.String(64))
    ars = db.Column(db.Float)
    usd = db.Column(db.Float)
    tag = db.Column(db.String(128), index=True)

    item_payment = db.Column(db.Integer, db.ForeignKey('creditpayments.id'))

    def __repr__(self):
        return '<Credit {}>'.format(self.id)


class CreditPayments(db.Model):
    __tablename__ = 'creditpayments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_number = db.Column(db.Integer, db.ForeignKey('creditcard.card_number'))
    due_date = db.Column(db.DateTime)
    # id for card payments entries in balance
    card_payment = db.Column(db.Integer, db.ForeignKey('balance.id'))
    # id for items in card invoice
    item_payment = db.relationship('Credit', backref='item_payed', lazy='dynamic')



    def __repr__(self):
        return '<Payment {} {}>'.format(self.card_number, self.due_date.date())