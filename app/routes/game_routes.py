from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import current_user, login_required
from app import db
from app.models import Question, GameData, AnsweredQuestion
import time
from random import randint, shuffle

game = Blueprint('game', __name__)

# Helper function to get or create active game data
def get_or_create_active_game_data(user_id):
    game_data = GameData.query.filter_by(user_id=user_id, is_active=True).first()
    if game_data is None:
        game_data = GameData(user_id=user_id, stage=1, progress=0, score=0)
        db.session.add(game_data)
        db.session.commit()
    return game_data

# Helper function to get unanswered question
def get_unanswered_question(category, answered_question_ids):
    return Question.query.filter(Question.category == category, Question.id.notin_(answered_question_ids)) \
        .order_by(db.func.random()).first()

# Helper function to update the score
def update_score(user_id, roll):
    game_data = GameData.query.filter_by(user_id=user_id, is_active=True).first()
    if game_data.score is None:
        game_data.score = 0

    game_data.progress += 1

    if game_data.stage == 2 and roll > 0:
        roll = -roll
    game_data.score += roll

    db.session.commit()

# Helper function to get opposite face of dice
def get_opposite_face(roll):
    return 7 - roll

# Route to select a category
@game.route('/select_category')
@login_required
def select_category():
    if not Question.query.first():
        flash('هیچ سوالی در پایگاه داده موجود نیست.', 'info')
        return redirect(url_for('main.home'))

    game_data = get_or_create_active_game_data(current_user.id)

    return render_template('select_category.html', title='انتخاب دسته‌بندی', stage=game_data.stage,
                           progress=game_data.progress, score=game_data.score)

# Route to get a question from selected category
@game.route("/question/<category>")
@login_required
def question(category):
    if not Question.query.filter_by(category=category).first():
        flash('هیچ سوالی در این دسته‌بندی موجود نیست.', 'info')
        return redirect(url_for('game.select_category'))

    game_data = get_or_create_active_game_data(current_user.id)
    answered_questions = AnsweredQuestion.query.filter_by(user_id=current_user.id, game_data_id=game_data.id).all()
    answered_question_ids = [aq.question_id for aq in answered_questions]

    question = get_unanswered_question(category, answered_question_ids)

    if question is None:
        flash('تمامی سوالات این دسته‌بندی را پاسخ داده‌اید.', 'info')
        return redirect(url_for('game.select_category'))

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

# Route to handle the answer submission
@game.route("/answer", methods=['POST'])
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

    # Handle stage progression
    if game_data.progress == 25:
        if game_data.stage == 1:
            game_data.stage = 2
        else:
            game_data.stage = 1
            game_data.is_active = False
            new_game_data = GameData(user_id=current_user.id, stage=1, progress=0, score=0, is_active=True)
            db.session.add(new_game_data)
        game_data.progress = 0
        db.session.commit()
        flash('مرحله به پایان رسید! به مرحله بعد می‌روید.', 'info')
        return redirect(url_for('game.select_category'))

    return redirect(url_for('game.select_category'))

# Route to show current game result
@game.route("/result")
@login_required
def result():
    game_data = GameData.query.filter_by(user_id=current_user.id, is_active=True).first()
    return render_template('result.html', title='نتیجه', game_data=game_data)

# Route to show final result after game ends
@game.route("/final_result")
@login_required
def final_result():
    score = request.args.get('score', type=int)
    return render_template('final_result.html', title='نتیجه نهایی', score=score)
