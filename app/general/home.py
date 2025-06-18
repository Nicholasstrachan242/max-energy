from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound

home_bp = Blueprint('home', __name__)

# default route
@home_bp.route('/')
def home_page():
    try: return render_template('index.html')
    except TemplateNotFound: 
        abort(404)

# HTTP 429 - Too Many Requests - rate limit
@home_bp.route('/too-many-requests')
def too_many_requests_page():
    try: return render_template('429.html')
    except TemplateNotFound:
        abort(404)
        