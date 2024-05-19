import json
from app import create_app, db
from app.models import Question

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

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        import_questions('data/questions.json')
        print("Questions imported successfully!")
