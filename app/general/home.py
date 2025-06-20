from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound

home_bp = Blueprint('home', __name__)

# default route
@home_bp.route('/')
def home_page():
    try: return render_template('index.html')
    except TemplateNotFound: 
        abort(404)

# HTTP 403 - Forbidden
@home_bp.route('/access-forbidden')
def forbidden_page():
    try: return render_template('403.html')
    except TemplateNotFound:
        abort(404)

# HTTP 429 - Too Many Requests - rate limit
@home_bp.route('/too-many-requests')
def too_many_requests_page():
    try: return render_template('429.html')
    except TemplateNotFound:
        abort(404)

# HTTP 500 - Internal Server Error
@home_bp.route('/request-failed')
def server_error_page():
    try: return render_template('500.html')
    except TemplateNotFound:
        abort(404)