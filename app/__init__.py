import os, logging, platform
from logging.handlers import TimedRotatingFileHandler
from flask import Flask, jsonify, request, redirect
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from datetime import timedelta
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables
# load .env.test for testing, .env for production

app_env = os.getenv('APP_ENV', 'prod').lower()
if app_env in ['test', 'testing']:
    # enable override here to ensure .env.test gets loaded
    load_dotenv('.env.test', override=True)
else:
    load_dotenv('.env.prod')

# show which .env file loaded
print("loaded environment: ",app_env)
print("Loaded DB_USER:", os.getenv("DB_USER"))
print("Loaded DB_NAME:", os.getenv("DB_NAME"))


# initialize SQLAlchemy and Migrate
class Base(DeclarativeBase): pass
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# initialize CSRFProtect
csrf = CSRFProtect()

# determine what storage is used for rate limiting. 
# default to in-memory for Windows and testing. For production linux, use redis server.
storage_uri = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
# Limiter constructor
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=storage_uri
)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # determine if testing.
    env = os.getenv('APP_ENV', 'production').lower()
    is_testing = env in ['test', 'testing']

    # default config (FOR PRODUCTION)
    config = {
            # USING LOCAL MYSQL SERVER FOR TESTING

            # pass in variables from .env.
            # .env file not tracked by git. Create it manually.
            
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'SQLALCHEMY_DATABASE_URI': (
                f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
                f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
            ),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,

            # Cookie settings
            # 'SESSION_COOKIE_SECURE': True, # session cookie only uses https
            # 'REMEMBER_COOKIE_SECURE': True, # remember me cookie only uses https
            'SESSION_COOKIE_HTTPONLY': True, # prevents JS from accessing session cookie
            'SESSION_COOKIE_SAMESITE': 'Lax', # helps prevent CSRF attacks
            'REMEMBER_COOKIE_HTTPONLY': True, # prevents JS from accessing remember me cookie
            'REMEMBER_COOKIE_DURATION': timedelta(days=2),
            'REMEMBER_COOKIE_SAMESITE': 'Lax', # helps prevent CSRF attacks
            'WTF_CSRF_ENABLED': True, # enable CSRF protection

    }

    # Overwrite config for testing
    if is_testing: 
        config.update({
            'TESTING': True,
            'SESSION_COOKIE_SECURE': False, # allow http in test
            'REMEMBER_COOKIE_SECURE': False, # allow http in test
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'WTF_CSRF_ENABLED': False, 
            'EMAIL_ENCRYPTION_KEY': 'dHuevh04hI1Pn0ITPXmkka_sn-o3-5R9hCNkG_XbAN4=', # for testing only
            'SECRET_KEY': 'devkey' # used for session & csrf
        })

    # allow test config to override default config
    if test_config:
        config.update(test_config)

    # check uri for testing
    print("SQLALCHEMY_DATABASE_URI:", config['SQLALCHEMY_DATABASE_URI'])

    # pass in config
    app.config.from_mapping(config)

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # initialize login manager
    from app.auth.auth import init_login_manager
    init_login_manager(app)

    # initialize flask-limiter
    limiter.init_app(app)

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

    # custom error handling
    from app.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app
