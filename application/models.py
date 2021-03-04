from application import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    account = db.relationship('Account', backref='account', lazy='dynamic')

    def __repr__(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Account(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    bank = db.Column(db.String(64))
    account_n = db.Column(db.String(120), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    detail = db.Column(db.String(128))  
    flow = db.Column(db.Integer, index=True)
    bal = db.Column(db.Integer, index=True)
    tag = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Account {}>'.format(self.account_n)