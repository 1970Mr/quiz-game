import json
import os
import sys
from sqlalchemy import inspect
from dotenv import load_dotenv
from app import create_app, db, bcrypt
from app.models import User, Question, GameData, AnsweredQuestion

# Load environment variables from .env file
load_dotenv()

app = create_app()
app.app_context().push()


def import_questions(json_file, add_only):
    if not add_only:
        # Clear existing questions
        db.session.query(AnsweredQuestion).delete()
        db.session.query(Question).delete()
        db.session.query(GameData).delete()
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


def table_exists(table_name):
    inspector = inspect(db.engine)
    return inspector.has_table(table_name)


def create_admin():
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')

    if admin_username and admin_email and admin_password:
        # Check if admin user already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            admin_user = User(username=admin_username, email=admin_email, password=hashed_password, is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        if len(sys.argv) < 2:
            print("Usage: python script.py <path_to_json_file> [--add-only]")
            sys.exit(1)

        json_file_path = sys.argv[1]
        add_only = '--add-only' in sys.argv

        if not os.path.exists(json_file_path):
            print(f"File {json_file_path} does not exist.")
            sys.exit(1)

        tables = db.metadata.tables.keys()

        # Check if the tables exist
        if not all(table_exists(table) for table in tables):
            db.create_all()
            import_questions(json_file_path, add_only)
            create_admin()
            print("All tables created, questions imported, and admin user created successfully!")
        else:
            if not add_only:
                # Drop and recreate only the non-user tables
                if table_exists('question'):
                    Question.__table__.drop(db.engine)
                if table_exists('game_data'):
                    GameData.__table__.drop(db.engine)
                if table_exists('answered_question'):
                    AnsweredQuestion.__table__.drop(db.engine)

                Question.__table__.create(db.engine)
                GameData.__table__.create(db.engine)
                AnsweredQuestion.__table__.create(db.engine)

            import_questions(json_file_path, add_only)
            print("Questions imported successfully!")
