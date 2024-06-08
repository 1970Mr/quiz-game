from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import current_user, login_required
from app import db
from app.models import Question, GameData, AnsweredQuestion
import time
from random import randint, shuffle
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

game = Blueprint('game', __name__)

# Constants for categories and number of questions per stage
CATEGORIES = ["general", "math"]
NUM_QUESTIONS_PER_STAGE = int(os.getenv('NUM_QUESTIONS_PER_STAGE', '25'))


# Helper function to get or create active game data
def get_or_create_active_game_data(user_id):
    game_data = GameData.query.filter_by(user_id=user_id, is_active=True).first()
    if not game_data:
        game_data = GameData(user_id=user_id, stage=1, progress=0, score=0)
        db.session.add(game_data)
        db.session.commit()
    return game_data


# Helper function to get an unanswered question
def get_unanswered_question(category, answered_question_ids):
    return Question.query.filter(
        Question.category == category,
        Question.id.notin_(answered_question_ids)
    ).order_by(db.func.random()).first()


# Helper function to calculate the opposite face of a dice roll
def get_opposite_face(roll):
    return 7 - roll


# Helper function to update the score
def update_score(game_data, roll, category):
    opposite_face = get_opposite_face(abs(roll))
    if game_data.stage == 2:
        if roll < 0:
            game_data.score += roll
            return roll
        roll = -abs(roll)
        opposite_face = -abs(opposite_face)
    elif game_data.stage == 1 and roll <= 0:
        return 0

    if category == CATEGORIES[0]:
        game_data.score += roll
        return roll
    else:
        game_data.score += opposite_face
        return opposite_face


# Route to select a category
@game.route('/select_category')
@login_required
def select_category():
    if not Question.query.first():
        flash('هیچ سوالی در پایگاه داده موجود نیست.', 'info')
        return redirect(url_for('main.home'))

    game_data = get_or_create_active_game_data(current_user.id)
    return render_template('select_category.html', title='انتخاب دسته‌بندی', stage=game_data.stage,
                           progress=game_data.progress, score=game_data.score, num_questions=NUM_QUESTIONS_PER_STAGE)


# Route to get a question from selected category
@game.route("/question/<category>")
@login_required
def question(category):
    if not Question.query.filter_by(category=category).first():
        flash('هیچ سوالی در این دسته‌بندی موجود نیست.', 'info')
        return redirect(url_for('game.select_category'))

    game_data = get_or_create_active_game_data(current_user.id)
    answered_question_ids = [aq.question_id for aq in AnsweredQuestion.query.filter_by(
        user_id=current_user.id, game_data_id=game_data.id).all()]

    question = get_unanswered_question(category, answered_question_ids)
    if not question:
        flash('تمامی سوالات این دسته‌بندی را پاسخ داده‌اید.', 'info')
        return redirect(url_for('game.select_category'))

    session.update({
        'current_category': category,
        'question_id': question.id,
        'start_time': time.time(),
        'dice_roll': randint(1, 6)
    })

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
    current_time = time.time()

    game_data = get_or_create_active_game_data(current_user.id)
    category = session.get('current_category')

    # Check if the question has already been answered in the current game
    answered_question = AnsweredQuestion.query.filter_by(user_id=current_user.id, question_id=question_id,
                                                         game_data_id=game_data.id).first()
    if answered_question:
        flash('شما قبلا به این سوال پاسخ داده‌اید.', 'info')
        return redirect(url_for('game.select_category'))

    if selected_answer == question.correct_answer:
        flash(f'پاسخ درست بود! وجه بالای تاس {dice_roll} و وجه پایین تاس {get_opposite_face(dice_roll)} است.',
              'success')
        answer_score = update_score(game_data, dice_roll, category)
        answered_correctly = True
    elif session.get('start_time') and current_time - session['start_time'] > 25:
        flash('زمان شما به پایان رسید!', 'danger')
        answer_score = update_score(game_data, -6, category)
        answered_correctly = False
        selected_answer = selected_answer or 'زمان به اتمام رسید!'
    else:
        flash('نادرست!', 'danger')
        answer_score = update_score(game_data, -6, category)
        answered_correctly = False
        selected_answer = selected_answer or 'خالی ارسال شد!'

    db.session.add(AnsweredQuestion(
        user_id=current_user.id,
        game_data_id=game_data.id,
        question_id=question_id,
        question_text=question.question_text,
        selected_answer=selected_answer,
        correct_answer=question.correct_answer,
        answered_correctly=answered_correctly,
        dice_roll=dice_roll,
        answer_score=answer_score
    ))
    db.session.commit()

    game_data.progress += 1
    db.session.commit()

    if game_data.progress == NUM_QUESTIONS_PER_STAGE:
        if game_data.stage == 1:
            game_data.stage, game_data.progress = 2, 0
            flash('مرحله به پایان رسید! به مرحله بعد می‌روید.', 'info')
        else:
            game_data.is_active = False
            new_game_data = GameData(user_id=current_user.id, stage=1, progress=0, score=0, is_active=True)
            db.session.add(new_game_data)
            flash('بازی به پایان رسید!', 'info')
            db.session.commit()
            return redirect(url_for('game.final_result', score=game_data.score))

    db.session.commit()
    return redirect(url_for('game.select_category'))


# Route to show current game result
@game.route("/result")
@login_required
def result():
    game_data = get_or_create_active_game_data(current_user.id)
    return render_template('result.html', title='نتیجه', game_data=game_data, num_questions=NUM_QUESTIONS_PER_STAGE)


# Route to show final result after game ends
@game.route("/final_result")
@login_required
def final_result():
    score = request.args.get('score', type=int)
    return render_template('final_result.html', title='نتیجه نهایی', score=score)
