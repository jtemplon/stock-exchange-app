from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Stock, Holding
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app import db
from flask_login import current_user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')	

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please user a difference username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please user a different email address.')

def stock_choices():
    return db.session.query(Stock).all()

class TransactionForm(FlaskForm):
    stock = QuerySelectField('Stock', query_factory=stock_choices, validators=[DataRequired()])
    shares = IntegerField('Shares', validators=[DataRequired()])
    transactions = [("buy", "Buy"), ("sell", "Sell")]
    buy_or_sell = RadioField('Transaction Type', choices=transactions, validators=[DataRequired()])
    submit = SubmitField('Complete Transaction')
    
    def validate_shares(self, shares):
        if self.buy_or_sell.data == "buy":
            if current_user.cash < (shares.data * self.stock.data.price):
                raise ValidationError('You cannot afford this many shares.')
        elif self.buy_or_sell.data == "sell":
            holding = Holding.query\
                .filter_by(
                    user_id=current_user.id, 
                    stock=self.stock.data.name
                ).first()
            if holding:
                if shares.data > holding.shares:
                    raise ValidationError('You do not own enough of this team.')
            else:
                raise ValidationError('You do not own this team.')
        
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Request Password Reset')