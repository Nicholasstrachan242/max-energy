import os
import pymysql
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# initialize SQLAlchemy
db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # TESTING FLAG
    # ================================================
    TESTING = True
    # ================================================

    # configure db connection for test and prod
    if TESTING:
        config = {
            # USE LOCAL MYSQL SERVER
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            'SQLALCHEMY_DATABASE_URI': (
                f"mysql+pymysql://{os.getenv('TEST_DB_USER')}:{os.getenv('TEST_DB_PASS')}"
                f"@{os.getenv('TEST_DB_HOST')}:{os.getenv('TEST_DB_PORT')}/{os.getenv('TEST_DB_NAME')}"
            ),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }
    else:
        config = {
            # PRODUCTION CONFIG HERE
        }

    # pass in config
    app.config.from_mapping(config)

    # initialize the app with the extension
    db.init_app(app)

    print('DB connection established.')

    # check if instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from app.general.home import home_bp as home
    from app.auth.auth import auth_bp as auth

    app.register_blueprint(home)
    app.register_blueprint(auth)

    return app

