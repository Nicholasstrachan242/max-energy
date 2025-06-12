from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

home_bp = Blueprint('home', __name__)
login_bp = Blueprint('login', __name__)

# default route
@home_bp.route('/')
def home():
    try: return render_template('index.html')
    except TemplateNotFound: 
        abort(404)

# to do - handle login POST request. Use authorization.
@login_bp.route('/login', methods=['POST'])
def login():
    try:
        return render_template('login.html')
    except TemplateNotFound: 
        abort(404)
    