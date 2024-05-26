from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User, Question, GameData, AnsweredQuestion
from app.forms import RegistrationForm, LoginForm, UploadFileForm
from random import randint, shuffle
import time
import os
import json

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
        user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('حساب شما ایجاد شد! اکنون می‌توانید وارد شوید.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='ثبت نام', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.select_category'))
        else:
            flash('ورود ناموفق. لطفاً ایمیل و رمز عبور را بررسی کنید.', 'danger')
    return render_template('login.html', title='ورود', form=form)

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/select_category')
@login_required
def select_category():
    if not Question.query.first():
        flash('هیچ سوالی در پایگاه داده موجود نیست.', 'info')
        return redirect(url_for('main.home'))

    game_data = GameData.query.filter_by(user_id=current_user.id, is_active=True).first()
    if game_data is None:
        game_data = GameData(user_id=current_user.id, stage=1, progress=0, score=0)
        db.session.add(game_data)
        db.session.commit()

    return render_template('select_category.html', title='انتخاب دسته‌بندی', stage=game_data.stage,
                           progress=game_data.progress, score=game_data.score)

@main.route("/question/<category>")
@login_required
def question(category):
    if not Question.query.filter_by(category=category).first():
        flash('هیچ سوالی در این دسته‌بندی موجود نیست.', 'info')
        return redirect(url_for('main.select_category'))

    game_data = GameData.query.filter_by(user_id=current_user.id, is_active=True).first()
    answered_questions = AnsweredQuestion.query.filter_by(user_id=current_user.id, game_data_id=game_data.id).all()
    answered_question_ids = [aq.question_id for aq in answered_questions]

    question = Question.query.filter(Question.category == category, Question.id.notin_(answered_question_ids)).order_by(
        db.func.random()).first()

    if question is None:
        flash('تمامی سوالات این دسته‌بندی را پاسخ داده‌اید.', 'info')
        return redirect(url_for('main.select_category'))

    session['current_category'] = category
    session['question_id'] = question.id
    session['start_time'] = time.time()
    session['dice_roll'] = randint(1, 6)

    answers = [
        (question.correct_answer, True),
        (question.wrong_answer1, False),
        (question.wrong_answer2, False),
        (question.wrong_answer3, False)
    ]
    shuffle(answers)

    return render_template('question.html', title='سوال', question=question, answers=answers)

def get_opposite_face(roll):
    return 7 - roll

@main.route("/answer", methods=['POST'])
@login_required
def answer():
    question_id = session.get('question_id')
    question = Question.query.get(question_id)
    selected_answer = request.form.get('answer')
    dice_roll = session.get('dice_roll')
    start_time = session.get('start_time')
    current_time = time.time()

    if start_time and current_time - start_time > 25:
        flash('زمان شما به پایان رسید! ۶ امتیاز از شما کسر شد.', 'danger')
        update_score(current_user.id, -6)
        answered_correctly = False
    elif selected_answer == question.correct_answer:
        opposite_face = get_opposite_face(dice_roll)
        flash(f'پاسخ درست بود! شما تاس {dice_roll} را انداختید. وجه مقابل آن {opposite_face} است.', 'success')
        update_score(current_user.id, dice_roll)
        answered_correctly = True
    else:
        flash('نادرست! ۶ امتیاز از شما کسر شد.', 'danger')
        update_score(current_user.id, -6)
        answered_correctly = False

    game_data = GameData.query.filter_by(user_id=current_user.id, is_active=True).first()
    answered_question = AnsweredQuestion(
        user_id=current_user.id,
        question_id=question_id,
        game_data_id=game_data.id,
        answered_correctly=answered_correctly,
        selected_answer=selected_answer,
        correct_answer=question.correct_answer,
        dice_roll=dice_roll,
        question_text=question.question_text
    )
    db.session.add(answered_question)
    db.session.commit()

    if game_data.progress == 30 and game_data.stage == 1:
        game_data.progress = 0
        game_data.stage = 2
        db.session.commit()
        flash('مرحله ۱ به پایان رسید! به مرحله ۲ می‌روید.', 'info')
        return redirect(url_for('main.select_category'))
    elif game_data.progress == 30 and game_data.stage == 2:
        game_data.progress = 0
        game_data.stage = 1
        score = game_data.score
        game_data.is_active = False
        new_game_data = GameData(user_id=current_user.id, stage=1, progress=0, score=0, is_active=True)
        db.session.add(new_game_data)
        db.session.commit()
        flash('مرحله ۲ به پایان رسید! بازی به پایان رسید و آزمون جدید ایجاد شد.', 'info')
        return redirect(url_for('main.final_result', score=score))

    return redirect(url_for('main.select_category'))

def update_score(user_id, roll):
    game_data = GameData.query.filter_by(user_id=user_id, is_active=True).first()
    if game_data.score is None:
        game_data.score = 0

    game_data.progress += 1

    if game_data.stage == 2 and roll > 0:
        roll = -roll
    game_data.score += roll

    db.session.commit()

@main.route("/result")
@login_required
def result():
    game_data = GameData.query.filter_by(user_id=current_user.id, is_active=True).first()
    return render_template('result.html', title='نتیجه', game_data=game_data)

@main.route("/final_result")
@login_required
def final_result():
    score = request.args.get('score', type=int)
    return render_template('final_result.html', title='نتیجه نهایی', score=score)

@main.route("/admin/completed_games")
@login_required
def completed_games():
    if not current_user.is_admin:
        flash('شما دسترسی به این صفحه ندارید.', 'danger')
        return redirect(url_for('main.home'))

    completed_games = GameData.query.filter_by(is_active=False).order_by(GameData.id.desc()).all()
    return render_template('completed_games.html', title='بازی‌های تکمیل شده', completed_games=completed_games)


@main.route("/admin/upload_questions", methods=['GET', 'POST'])
@login_required
def upload_questions():
    if not current_user.is_admin:
        flash('شما دسترسی به این صفحه ندارید.', 'danger')
        return redirect(url_for('main.home'))

    form = UploadFileForm()
    if form.validate_on_submit():
        if form.file.data:
            # Define the uploads directory
            upload_folder = os.path.join('uploads', 'data')
            # Check if the directory exists, if not, create it
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            filename = form.file.data.filename
            filepath = os.path.join(upload_folder, filename)
            form.file.data.save(filepath)
            try:
                import_questions(filepath, form.add_only.data)
                flash('سوالات با موفقیت بارگذاری شدند.', 'success')
            except Exception as e:
                flash(f'خطایی رخ داد: {e}', 'danger')

    return render_template('upload_questions.html', title='بارگذاری سوالات', form=form)

def import_questions(json_file, add_only):
    if not add_only:
        # Clear existing questions
        db.session.query(Question).delete()
        db.session.commit()

    with open(json_file, 'r') as file:
        questions = json.load(file)

    for q in questions:
        question = Question(
            category=q['category'],
            question_text=q['question_text'],
            correct_answer=q['correct_answer'],
            wrong_answer1=q['wrong_answer1'],
            wrong_answer2=q['wrong_answer2'],
            wrong_answer3=q['wrong_answer3']
        )
        db.session.add(question)

    db.session.commit()
