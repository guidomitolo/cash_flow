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

    def __repr__(self):
        return '<Account nro. {}>'.format(self.account_n)


class Credit(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    bank = db.Column(db.String(64))
    card = db.Column(db.String(64))
    card_number = db.Column(db.Integer, index=True)
    expiration = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, index=True)
    creditor = db.Column(db.String(128))  
    share = db.Column(db.Integer)
    ars = db.Column(db.Integer)
    usd = db.Column(db.String(128))
    tag = db.Column(db.String(128), index=True)

    def __repr__(self):
        return '<Credit {}>'.format(self.user_id)