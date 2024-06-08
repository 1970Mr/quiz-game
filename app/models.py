from datetime import datetime
from app import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    game_data = db.relationship('GameData', backref='player', lazy=True)
    answered_questions = db.relationship('AnsweredQuestion', backref='user', lazy=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    wrong_answer1 = db.Column(db.String(100), nullable=False)
    wrong_answer2 = db.Column(db.String(100), nullable=False)
    wrong_answer3 = db.Column(db.String(100), nullable=False)


class GameData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stage = db.Column(db.Integer, nullable=False, default=1)
    progress = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, default=True)


class AnsweredQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_data_id = db.Column(db.Integer, db.ForeignKey('game_data.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    question_text = db.Column(db.String, nullable=False)
    selected_answer = db.Column(db.String(256), nullable=False)
    correct_answer = db.Column(db.String, nullable=False)
    answered_correctly = db.Column(db.Boolean, nullable=False, default=False)
    dice_roll = db.Column(db.Integer, nullable=False)
    answer_score = db.Column(db.Integer, nullable=False, default=0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
