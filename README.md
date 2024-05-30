# Quiz Game

Welcome to Quiz Game! This is a simple Flask web application where users can play a quiz game by answering multiple-choice questions.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/1970Mr/quiz-game.git
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

## Configuration

Create a .env file in the root directory of the project and set the following environment variables. You can use the provided .env.example file as a template:
```
ADMIN_USERNAME=your_admin_username
ADMIN_EMAIL=your_admin_email
ADMIN_PASSWORD=your_admin_password
```

## Usage

### Seed Initial Data

You can seed initial data into the database, which includes creating the necessary tables and importing questions from a JSON file:

```bash
python initial_data.py path_to_json_file [--add-only]
```

- `path_to_json_file`: The path to the JSON file containing the questions.
- `--add-only`: Optional flag to add new questions without resetting the existing ones.

For example:

```bash
python initial_data.py data/questions.json
```

If you want to add questions to the existing ones without resetting:

```bash
python initial_data.py data/questions.json --add-only
```

## Running the Application

After seeding the initial data or importing questions, you can run the Flask application:

```bash
flask run
```

Then, open your web browser and go to [http://localhost:5000/](http://localhost:5000/) to access the Quiz Game.

## Running with Docker Compose

You can also run the application using Docker and Docker Compose. This approach ensures that you don't need to manually set up a virtual environment or install dependencies locally.

### Steps:

1. Build and run the Docker container:

    ```bash
    docker-compose up --build
    ```

2. After the container is up and running, open your web browser and go to [http://localhost:5000/](http://localhost:5000/) to access the Quiz Game.

## Credits

This project was created as a learning exercise by MR.1970. Feel free to contribute or use it as a basis for your own projects.
