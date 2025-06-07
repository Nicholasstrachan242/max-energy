import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash

# this import is for when database is added
#  from app.db import get_db

# auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
login_bp = Blueprint('login', __name__)

@login_bp.route('/login')
def login():
    try:
        return render_template('login.html')
    except TemplateNotFound:
        abort(404)