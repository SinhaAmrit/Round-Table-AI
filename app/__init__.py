from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()
# Initialize LoginManager
login_manager = LoginManager()

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask app: The configured Flask application.
    """
    # Create the Flask app
    app = Flask(__name__, static_folder='../static', template_folder="../templates")

    # Configure Flask app using environment variables
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    # Initialize the database
    db.init_app(app)

    # Register blueprints for different parts of the application
    from .views import views
    from .auth import auth
    from .discussion import disc
    from .account import acc
    from .forms import form

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(disc, url_prefix='/')
    app.register_blueprint(acc, url_prefix='/')
    app.register_blueprint(form, url_prefix='/')

    # Import User model
    from .models import User

    with app.app_context():
        db.create_all()

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        """
        Load a user from the User model based on the user ID.

        Args:
            id (str): User ID.

        Returns:
            User: User object.
        """
        return User.query.get(id)

    return app
