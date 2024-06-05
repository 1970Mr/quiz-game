from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.config import Config
import os
from dotenv import load_dotenv
from sqlalchemy import inspect

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'
login_manager.login_message = "لطفاً برای دسترسی به این صفحه وارد شوید."

def create_admin():
    from app.models import User
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

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import create_blueprints
    create_blueprints(app)

    with app.app_context():
        # Check if the database is empty
        inspector = inspect(db.engine)
        if not inspector.get_table_names():
            db.create_all()
            print("Database is empty, all tables created.")
            create_admin()

    return app
