import json
import os
import sys
from sqlalchemy import inspect
from app import create_app, db, create_admin
from app.models import Question, GameData, AnsweredQuestion

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
