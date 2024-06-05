from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required
from app import db
from app.models import GameData, AnsweredQuestion, Question
from app.forms import UploadFileForm
import os
import json
import pandas as pd
from flask import send_file
from io import BytesIO

admin = Blueprint('admin', __name__)


@admin.route("/admin/completed_games")
@login_required
def completed_games():
    if not current_user.is_admin:
        flash('شما دسترسی به این صفحه ندارید.', 'danger')
        return redirect(url_for('main.home'))

    completed_games = GameData.query.filter_by(is_active=False).order_by(GameData.id.desc()).all()
    return render_template('completed_games.html', title='بازی‌های تکمیل شده', completed_games=completed_games)


@admin.route("/admin/game_details/<int:game_id>")
@login_required
def game_details(game_id):
    if not current_user.is_admin:
        flash('شما دسترسی به این صفحه ندارید.', 'danger')
        return redirect(url_for('main.home'))

    game_data = GameData.query.get_or_404(game_id)
    answered_questions = AnsweredQuestion.query.filter_by(game_data_id=game_id).all()
    return render_template('game_details.html', title='جزئیات بازی', game_data=game_data,
                           answered_questions=answered_questions)


@admin.route("/admin/upload_questions", methods=['GET', 'POST'])
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


@admin.route("/admin/export_completed_games")
@login_required
def export_completed_games():
    if not current_user.is_admin:
        flash('شما دسترسی به این صفحه ندارید.', 'danger')
        return redirect(url_for('main.home'))

    completed_games = GameData.query.filter_by(is_active=False).order_by(GameData.id.desc()).all()
    data = []
    for game in completed_games:
        data.append({
            'نام کاربری': game.player.username,
            'ایمیل': game.player.email,
            'امتیاز': game.score
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Completed Games')
    writer.close()
    output.seek(0)

    return send_file(output, download_name='completed_games.xlsx', as_attachment=True)


@admin.route("/admin/export_game_details/<int:game_id>")
@login_required
def export_game_details(game_id):
    if not current_user.is_admin:
        flash('شما دسترسی به این صفحه ندارید.', 'danger')
        return redirect(url_for('main.home'))

    GameData.query.get_or_404(game_id)
    answered_questions = AnsweredQuestion.query.filter_by(game_data_id=game_id).all()
    data = []
    for aq in answered_questions:
        data.append({
            'سوال': aq.question_text,
            'پاسخ داده شده': aq.selected_answer,
            'پاسخ صحیح': aq.correct_answer,
            'تاس': aq.dice_roll,
            'درست/نادرست': 'درست' if aq.answered_correctly else 'نادرست'
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Game Details')
    writer.close()
    output.seek(0)

    return send_file(output, download_name=f'game_{game_id}_details.xlsx', as_attachment=True)
