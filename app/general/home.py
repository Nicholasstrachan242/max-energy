from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound

home_bp = Blueprint('home', __name__)

# default route
@home_bp.route('/')
def home_page():
    try: return render_template('index.html')
    except TemplateNotFound: 
        abort(404)
        