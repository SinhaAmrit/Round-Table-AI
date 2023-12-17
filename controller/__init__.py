from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

DB = 'This dict contains database credentials'

def create_app():
    app = Flask(__name__, static_folder='../static/js', template_folder="../templates")
    app.config['SECRET_KEY'] = 'reuighsjkdvfbskerh'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB['user']}:{DB['password']}@{DB['host']}:{DB['port']}/{DB['database']}"
    db.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    return app