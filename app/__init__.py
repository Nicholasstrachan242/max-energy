import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import timedelta

# Load environment variables
load_dotenv()

# initialize SQLAlchemy and Migrate
class Base(DeclarativeBase): pass
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# initialize LoginManager
login_manager = LoginManager()
# handle login messages for pages that require login
login_manager.login_message = "Please log in to view this page."
login_manager.login_message_category = "warning"

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # determine if testing.
    # TESTING FLAG IS IN .env
    env = os.getenv('APP_ENV', 'production').lower()
    is_testing = env in ['test', 'testing']

    # default config (FOR PRODUCTION)
    config = {
            # USING LOCAL MYSQL SERVER FOR TESTING

            # use .env for TEST_SECRET_KEY, TEST_DB_USER, 
            # TEST_DB_PASS, TEST_DB_HOST, 
            # TEST_DB_PORT, and TEST_DB_NAME
            # .env file not tracked by git. Create it manually.
            
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'SQLALCHEMY_DATABASE_URI': (
                f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
                f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
            ),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,

            # Cookie settings
            'SESSION_COOKIE_SECURE': True, # session cookie only uses https
            'REMEMBER_COOKIE_SECURE': True, # remember me cookie only uses https
            'SESSION_COOKIE_HTTPONLY': True, # prevents JS from accessing session cookie
            'SESSION_COOKIE_SAMESITE': 'Lax', # helps prevent CSRF attacks
            'REMEMBER_COOKIE_HTTPONLY': True, # prevents JS from accessing remember me cookie
            'REMEMBER_COOKIE_DURATION': timedelta(days=2),
            'REMEMBER_COOKIE_SAMESITE': 'Lax', # helps prevent CSRF attacks
            'WTF_CSRF_ENABLED': True, # enable CSRF protection TODO: finish setting up CSRF protection on pages with forms
    }

    # Overwrite config for testing
    if is_testing: 
        config.update({
            'TESTING': True,
            'SECRET_KEY': os.getenv('TEST_SECRET_KEY'),
            'SQLALCHEMY_DATABASE_URI': (
                f"mysql+pymysql://{os.getenv('TEST_DB_USER')}:{os.getenv('TEST_DB_PASS')}"
                f"@{os.getenv('TEST_DB_HOST')}:{os.getenv('TEST_DB_PORT')}/{os.getenv('TEST_DB_NAME')}"
            ),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'WTF_CSRF_ENABLED': False # disable CSRF protection for testing
        })

    # allow test config to override default config
    if test_config:
        config.update(test_config)

    # pass in config
    app.config.from_mapping(config)

    # initialize app with db connection. Create tables if they don't exist.
    db.init_app(app)
    migrate.init_app(app, db)

    # setup login manager
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
    from app.general.dashboard import dashboard_bp as dashboard
    from app.general.contact import contact_bp as contact
    from app.general.admin import admin_bp as admin
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(contact)
    app.register_blueprint(admin)


    return app
