import json
from sqlalchemy import inspect
from app import create_app, db
from app.models import User, Question, GameData, AnsweredQuestion

app = create_app()
app.app_context().push()


def import_questions(json_file):
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
        tables = db.metadata.tables.keys()

        # Check if the tables exist
        if not all(table_exists(table) for table in tables):
            db.create_all()
            import_questions('data/questions.json')
            print("All tables created and questions imported successfully!")
        else:
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
            import_questions('data/questions.json')
            print("Non-user tables recreated and questions imported successfully!")
