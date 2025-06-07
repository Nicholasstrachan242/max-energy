import os
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load instance config if it exists when not testing.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in.
        app.config.from_mapping(test_config)

    # ensure the instance folder exists.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from app.general.home import home_bp as home
    #from app.auth.auth import auth_bp as auth
    from app.auth.auth import login_bp as login
    
    app.register_blueprint(home)
    #app.register_blueprint(auth)
    app.register_blueprint(login)

    return app

