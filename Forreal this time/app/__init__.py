from flask import Flask
from db import db
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.auth_routes import auth_bp
from app.admin_routes import admin_bp
from app.main_routes import main_bp
import secrets

def create_app():
    app = Flask(__name__, static_folder='statics')
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    CSRFProtect(app)
    Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)
    return app 