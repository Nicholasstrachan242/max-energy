from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound
from flask_login import login_required

welcome_bp = Blueprint('welcome', __name__)

# default route
@welcome_bp.route('/welcome')
@login_required
def welcome_page():
    try: return render_template('welcome.html')
    except TemplateNotFound: 
        abort(404)