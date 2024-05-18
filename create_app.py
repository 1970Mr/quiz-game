from app import create_app, db
from app.models import User, GameData, Question

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
