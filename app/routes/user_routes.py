from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User
from app.forms import RegistrationForm, LoginForm

user = Blueprint('user', __name__)


@user.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('حساب شما ایجاد شد! اکنون می‌توانید وارد شوید.', 'success')
        return redirect(url_for('user.login'))
    return render_template('register.html', title='ثبت نام', form=form)


@user.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('game.select_category'))
        else:
            flash('ورود ناموفق. لطفاً ایمیل و رمز عبور را بررسی کنید.', 'danger')
    return render_template('login.html', title='ورود', form=form)


@user.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))
