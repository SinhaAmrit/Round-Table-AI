"""
The main initialization file for the Flask application.

This file creates the Flask app, sets up the database, and initializes Flask extensions.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import uuid

# Initialize the SQLAlchemy database object
db = SQLAlchemy()

def create_app():
    """
    Create and configure the Flask app.

    Returns:
        Flask: The configured Flask app.
    """
    app = Flask(__name__)

    # Database connection parameters
    db_params = {
        'user': 'postgres',
        'password': 'JHc0oWLiV2vcwsuu',
        'host': 'db.oufxvnabgnyidiwwiviq.supabase.co',
        'port': '5432',
        'database': 'postgres'
    }

    # Configure Flask app settings
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

    # Initialize the database with the app
    db.init_app(app)

    # Blueprint for auth routes in the app
    from src.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint for non-auth parts of the app
    from src.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Initialize Flask-Login extension
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(id):
        """
        Load a user given their ID.

        Args:
            id (str): The user ID.

        Returns:
            User: The User object corresponding to the given ID.
        """
        return User.query.get(uuid.UUID(id))

    return app
