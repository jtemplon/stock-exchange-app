from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, TransactionForm
from app.forms import ResetPasswordRequestForm, ResetPasswordForm
from app.email import send_password_reset_email
from app.models import User, Holding, Transaction
from datetime import datetime
from sqlalchemy import desc

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user', username=current_user.username)
        return redirect(url_for('user', username=current_user.username))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user', current_user))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check you email for the instructions to reset your password.')
        return redirect(url_for('login'))
    return render_template(
        'reset_password_request.html', 
        title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    holdings = Holding.query.filter_by(user_id=user.id)
    transactions = Transaction\
        .query\
        .filter_by(user_id=user.id)\
        .order_by(desc(Transaction.timestamp))\
        .limit(10)
    return render_template('user.html', user=user, holdings=holdings, transactions=transactions)

@app.route('/transaction', methods=['GET', 'POST'])
@login_required
def transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        holding = Holding.query.filter_by(user_id=current_user.id, stock=form.stock.data.name).first()
        if form.buy_or_sell.data == "buy":
            current_cash = current_user.cash - round((form.shares.data * form.stock.data.price), 2)
            current_user.cash = round(current_cash, 2)
            # If this is a new holding, create it
            if holding is None:
                new_holding = Holding(
                    stock=form.stock.data.name,
                    shares=form.shares.data,
                    purchase_price=form.stock.data.price,
                    user_id=current_user.id,
                    
                )
                db.session.add(new_holding)
            else:
                total_shares = holding.shares + form.shares.data
                holding.purchase_price = round((
                    (holding.purchase_price * holding.shares) +
                    (form.stock.data.price * form.shares.data)) / total_shares, 2)
                holding.shares = total_shares
                
        else:
            current_cash = current_user.cash + round((form.shares.data * form.stock.data.price), 2)
            current_user.cash = round(current_cash, 2)
            holding.shares = holding.shares - form.shares.data
        
        new_transaction = Transaction(
            team=form.stock.data.name,
            price=form.stock.data.price,
            shares=form.shares.data,
            user_id=current_user.id,
            timestamp=datetime.utcnow(),
            buy_or_sell=form.buy_or_sell.data
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash('Trade submitted!')
        return redirect(url_for('user', username=current_user.username))
    return render_template('transaction.html', title='Transaction', form=form)

@app.route('/leaders')
@login_required
def leaders():
    users = User.query.all()
    leaders = sorted(users, key=lambda x: x.portfolio_value, reverse=True)[:20]
    return render_template('leaders.html', title='Leaders', leaders=leaders)