from app import create_app, db
from app.models import User, Question, GameData
from flask_bcrypt import generate_password_hash
import random

app = create_app()
app.app_context().push()

def create_sample_users():
    users = [
        {"username": "user1", "email": "user1@example.com", "password": "password"},
        {"username": "user2", "email": "user2@example.com", "password": "password"},
        {"username": "user3", "email": "user3@example.com", "password": "password"},
    ]
    for user_data in users:
        hashed_password = generate_password_hash(user_data['password']).decode('utf-8')
        user = User(username=user_data['username'], email=user_data['email'], password=hashed_password)
        db.session.add(user)
    db.session.commit()

def create_sample_questions():
    categories = ['general', 'math']
    for category in categories:
        for i in range(150):  # 150 questions per category
            question = Question(
                category=category,
                question_text=f"Sample question {i+1} in {category} category?",
                correct_answer="Correct Answer",
                wrong_answer1="Wrong Answer 1",
                wrong_answer2="Wrong Answer 2",
                wrong_answer3="Wrong Answer 3"
            )
            db.session.add(question)
    db.session.commit()

def create_sample_game_data():
    users = User.query.all()
    for user in users:
        game_data = GameData(user_id=user.id, score=0, progress=0, stage=1)
        db.session.add(game_data)
    db.session.commit()

def seed_database():
    create_sample_users()
    create_sample_questions()
    create_sample_game_data()
    print("Database seeded successfully!")

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_database()
