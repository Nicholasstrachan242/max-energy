import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Load environment variables
load_dotenv()

# initialize SQLAlchemy
class Base(DeclarativeBase): pass
db = SQLAlchemy(model_class=Base)

# initialize LoginManager
login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # TESTING FLAG
    # ================================================
    TESTING = True
    # ================================================

    # configure db connection for test and prod
    if TESTING:
        config = {
            # USING LOCAL MYSQL SERVER FOR TESTING

            # use .env file for TEST_SECRET_KEY, TEST_DB_USER, 
            # TEST_DB_PASS, TEST_DB_HOST, 
            # TEST_DB_PORT, and TEST_DB_NAME
            # .env file not tracked by git. Create it manually.
            'SECRET_KEY': os.getenv('TEST_SECRET_KEY'),
            'SQLALCHEMY_DATABASE_URI': (
                f"mysql+pymysql://{os.getenv('TEST_DB_USER')}:{os.getenv('TEST_DB_PASS')}"
                f"@{os.getenv('TEST_DB_HOST')}:{os.getenv('TEST_DB_PORT')}/{os.getenv('TEST_DB_NAME')}"
            ),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    else:
        config = {
            # PRODUCTION DB CONFIG HERE
        }

    # pass in config
    app.config.from_mapping(config)

    # initialize app with db connection
    db.init_app(app)

    # initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.User import User
        return User.query.get(int(user_id))

    # check for instance folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # blueprints and routes
    from app.general.home import home_bp as home
    from app.auth.auth import auth_bp as auth
    from app.general.welcome import welcome_bp as welcome
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(welcome)

    return app

