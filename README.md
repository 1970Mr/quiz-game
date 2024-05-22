# Quiz Game

Welcome to Quiz Game! This is a simple Flask web application where users can play a quiz game by answering multiple-choice questions.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/github-1970/quiz-game.git
cd quiz-game
```

2. Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

4. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Seed Sample Data

You can seeding sample data into the database:

```bash
python seed.py
```

### Import Questions from JSON

You can also import questions from a JSON file into the database:

```bash
python load_data.py
```

## Running the Application

After seeding the sample data or importing questions, you can run the Flask application:

```bash
flask run
```

Then, open your web browser and go to [http://localhost:5000/](http://localhost:5000/) to access the Quiz Game.

## Credits

This project was created as a learning exercise by MR.1970. Feel free to contribute or use it as a basis for your own projects.
