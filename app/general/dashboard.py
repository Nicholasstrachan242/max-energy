from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound
from flask_login import login_required

dashboard_bp = Blueprint('dashboard', __name__)

# dashboard/welcome page route
@dashboard_bp.route('/dashboard')
@login_required
def dashboard_page():
    try: return render_template('dashboard.html')
    except TemplateNotFound: 
        abort(404)