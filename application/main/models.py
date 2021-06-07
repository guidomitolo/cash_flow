from application import db

class Balance(db.Model):
    __tablename__ = 'balance'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bank = db.Column(db.String(64))
    account_n = db.Column(db.String(120), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    detail = db.Column(db.String(128))  
    flow = db.Column(db.Integer)
    bal = db.Column(db.Integer)
    type = db.Column(db.String(128), index=True)
    id_statement = db.Column(db.Integer, db.ForeignKey('creditstatement.id'))

    def __repr__(self):
        return '<Account nro. {}>'.format(self.account_n)


class CreditCard(db.Model):
    __tablename__ = 'creditcard'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    number = db.Column(db.Integer, index=True)
    vendor = db.Column(db.String(64))
    bank = db.Column(db.String(64))
    expiration = db.Column(db.DateTime)

    credit = db.relationship('Credit', backref='transactions', lazy='dynamic')

    def __repr__(self):
        return '<Card {0} {1}>'.format(self.vendor, self.number)


class Credit(db.Model):
    __tablename__ = 'credit'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    statement = db.Column(db.Integer, db.ForeignKey('creditstatement.id'))
    card_number = db.Column(db.Integer, db.ForeignKey('creditcard.number'))
    # card_code printed in statement to be replaced by card number is completed
    card_code = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True)
    transaction = db.Column(db.String(128))  
    share = db.Column(db.String(64))
    purchase = db.Column(db.Float)
    currency = db.Column(db.String(64))
    type = db.Column(db.String(128), index=True)

    def __repr__(self):
        return '<Credit {}>'.format(self.id)


class CreditStatement(db.Model):
    __tablename__ = 'creditstatement'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    due_date = db.Column(db.DateTime)
    close_date = db.Column(db.DateTime)
    ars = db.Column(db.Float)
    usd = db.Column(db.Float)

    credit = db.relationship('Credit', backref='credit', lazy='dynamic')
    balance = db.relationship('Balance', backref='balance', lazy='dynamic')
    taxes = db.relationship('CreditTaxes', backref='credit_taxes', lazy='dynamic')

    def __repr__(self):
        return '<Statement {} {}>'.format(self.ars, self.close_date.date())


class CreditTaxes(db.Model):
    __tablename__ = 'credittaxes'

    id = db.Column(db.Integer, primary_key=True)
    statement = db.Column(db.Integer, db.ForeignKey('creditstatement.id'))
    type = db.Column(db.String(128))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(64))


    # funcion q haga la suman por cada statement?

    def __repr__(self):
        return '<Taxes {} {}>'.format(self.statement)