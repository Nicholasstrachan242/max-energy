import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import timedelta
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

# initialize CSRFProtect
csrf = CSRFProtect()

# initialize Limiter
limiter = Limiter(get_remote_address)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # determine if testing.
    # TESTING FLAG IS IN .env
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

  

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Flask-Limiter setup
    # Use w/ redis for production (linux) and as-is in-memory for testing (windows)
    if is_testing:
        limiter.init_app(app)
    else:
        redis_url = os.getenv('RATE_LIMIT_REDIS_URL', 'redis://localhost:6379/0')
        limiter.init_app(
            app,
            storage_uri=redis_url,
            default_limits=["200 per day", "50 per hour"]
        )

    # Error handling w/ json payloads, useful if making API
    """
    def register_error_handlers(app):
        # error 403 - Forbidden
        @app.errorhandler(403)
        def forbidden_handler(e):
            return jsonify(error="Forbidden. You are not authorized to access this page. If you believe this is in error, please contact IT support"), 403
        
        # error 404 - Not Found
        @app.errorhandler(404)
        def not_found_handler(e):
            return jsonify(error="Resource not found."), 404
        
        # error 429 - Rate Limit
        @app.errorhandler(429)
        def rate_limit_handler(e):
            return jsonify(error="Too many requests, please try again later."), 429
        
        # error 500 - Internal Server Error
        @app.errorhandler(500)
        def server_error_handler(e):
            return jsonify(error="Oops, something went wrong -- INTERNAL SERVER ERROR --"), 500
        
        # error 502 - Bad Gateway
        @app.errorhandler(502)
        def bad_gatweay_handler(e):
            return jsonify(error="Bad gateway."), 502
        
        # error 503 - Service Temporarily Unavailable
        @app.errorhandler(503)
        def service_unavailable_handler(e):
            return jsonify(error="Service temporarily unavailable."), 503
    """

    # setup login manager
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

    # jsonify error handler
    # register_error_handlers(app)

    return app
