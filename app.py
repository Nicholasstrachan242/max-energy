from flask import Flask, Blueprint
from routes import home_bp as home, login_bp as login

app = Flask(__name__)

app.register_blueprint(home)
app.register_blueprint(login)   

if __name__ == '__main__':
    app.run(debug=True)
