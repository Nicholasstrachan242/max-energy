import functools
from flask import Blueprint, redirect, render_template, request, session, url_for, abort
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.User import User
from flask_login import login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('home.home_page'))
            else:
                # error message
                error = 'Invalid email or password'
                return render_template('login.html', error=error)
        return render_template('login.html')
    except TemplateNotFound:
        abort(404)