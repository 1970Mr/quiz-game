from .main_routes import main
from .user_routes import user
from .game_routes import game
from .admin_routes import admin

def create_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(user)
    app.register_blueprint(game)
    app.register_blueprint(admin)
