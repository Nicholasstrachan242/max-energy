from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound

welcome_bp = Blueprint('welcome', __name__)

# default route
@welcome_bp.route('/welcome')
def welcome_page():
    try: return render_template('welcome.html')
    except TemplateNotFound: 
        abort(404)