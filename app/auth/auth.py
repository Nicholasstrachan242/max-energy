import functools
from flask import Blueprint, redirect, render_template, request, session, url_for, abort
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        #if request.method == 'POST':
        #    username = request.form['username']
        #    password = request.form['password']
        #    user = User.query.filter_by(username=username).first()
        #    if user and check_password_hash(user.password, password):
        #       session['user_id'] = user.id
        #       return redirect(url_for('home.index'))
        return render_template('login.html')
    except TemplateNotFound:
        abort(404)