from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    game_data = db.relationship('GameData', backref='player', lazy=True)

class GameData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    progress = db.Column(db.Integer, default=0, nullable=False)
    stage = db.Column(db.Integer, default=1, nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    question_text = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(100), nullable=False)
    wrong_answer1 = db.Column(db.String(100), nullable=False)
    wrong_answer2 = db.Column(db.String(100), nullable=False)
    wrong_answer3 = db.Column(db.String(100), nullable=False)
