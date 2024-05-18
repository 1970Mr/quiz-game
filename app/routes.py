from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Question, GameData
from app.forms import RegistrationForm, LoginForm
from random import randint

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.select_category'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route("/select_category")
@login_required
def select_category():
    return render_template('select_category.html', title='Select Category')

@main.route("/question/<category>")
@login_required
def question(category):
    question = Question.query.filter_by(category=category).order_by(db.func.random()).first()
    session['current_category'] = category
    session['question_id'] = question.id
    return render_template('question.html', title='Question', question=question)

@main.route("/answer", methods=['POST'])
@login_required
def answer():
    question_id = session.get('question_id')
    question = Question.query.get(question_id)
    selected_answer = request.form['answer']
    category = session.get('current_category')

    if selected_answer == question.correct_answer:
        roll = randint(1, 6)
        flash(f'Correct! You rolled a {roll}.', 'success')
        update_score(current_user.id, roll)
    else:
        flash('Incorrect! Try again.', 'danger')

    return redirect(url_for('main.select_category'))

def update_score(user_id, roll):
    game_data = GameData.query.filter_by(user_id=user_id).first()
    if game_data is None:
        # Handle the case where game_data is not found
        return
    
    if game_data.score is None:
        game_data.score = 0

    game_data.score += roll
    game_data.progress += 1

    if game_data.progress >= 30:
        if game_data.stage == 1:
            game_data.stage = 2
        elif game_data.stage == 2:
            game_data.stage = 1
        game_data.progress = 0

    db.session.commit()

@main.route("/result")
@login_required
def result():
    game_data = GameData.query.filter_by(user_id=current_user.id).first()
    return render_template('result.html', title='Result', game_data=game_data)
