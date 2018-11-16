from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from time import time
from app import app, db, login
from hashlib import md5
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import jwt

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Giving every Portfolio $500 to start
    cash = db.Column(db.Float, default=500.00)
    holdings = db.relationship('Holding', backref='owner', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='moves', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, 
                app.config['SECRET_KEY'], 
                algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
        
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'\
            .format(digest, size)
    
    @hybrid_property
    def portfolio_value(self):
        holdings_value = sum([ h.value for h in self.holdings ])
        return round(self.cash + holdings_value, 2)

class Holding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stock = db.Column(db.String(120), db.ForeignKey('stock.name'))
    shares = db.Column(db.Integer)
    # Note: If shares are purchased at multiple prices, this is an average
    purchase_price = db.Column(db.Float)
        
    def __repr__(self):
        return '<Holding {}>'.format(self.team)
    
    @hybrid_property
    def value(self):
        return round(self.shares * self.asset.price, 2)
    
    def value_change(self):
        return self.value - round(self.shares * self.purchase_price, 2)
    
    def value_change_str(self):
        return "${0:.2f}".format(self.value_change()).replace("$-", "-$")

class Stock(db.Model):
    name = db.Column(db.String(120), primary_key=True)
    price = db.Column(db.Float)
    holdings = db.relationship('Holding', backref='asset', lazy='dynamic')
        
    def __repr__(self):
        return '<Stock {}>'.format(self.name)
    
    def __str__(self):
        return "{}: ${:.2f}".format(self.name, self.price)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shares = db.Column(db.Integer)
    team = db.Column(db.String(120))
    price = db.Column(db.Float)
    buy_or_sell = db.Column(db.String(120))
    
    def __repr__(self):
        return '<Transaction {}>'.format(self.team)
    
    def total_cost(self):
        if self.buy_or_sell == "buy":
            return -(self.shares * self.price)
        return self.shares * self.price