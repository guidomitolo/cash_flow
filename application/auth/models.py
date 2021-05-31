from application import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    balance = db.relationship('Balance', backref='balance', lazy='dynamic')
    credit = db.relationship('Credit', backref='credit', lazy='dynamic')
    credit_card = db.relationship('Balance', backref='credit_card', lazy='dynamic')
    payments = db.relationship('Balance', backref='payments', lazy='dynamic')

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
