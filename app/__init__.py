import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # TESTING FLAG
    # ================================================
    TESTING = True
    # ================================================

    if TESTING:
        config = {
        'SECRET_KEY': os.getenv('SECRET_KEY'),
    }
    else:
        config = {
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'SQLALCHEMY_DATABASE_URI': (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        ),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False
    }

    # pass in config
    app.config.from_mapping(config)

    # initialize db
    #try:
        #db.init_app(app)
    #except Exception as e:
    #    print(f"Error initializing database: {e}")
    #    raise e

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

