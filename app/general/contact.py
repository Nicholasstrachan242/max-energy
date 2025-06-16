from flask import Blueprint, render_template, abort, current_app, request
from jinja2 import TemplateNotFound

contact_bp = Blueprint('contact', __name__)

# contact us page route
@contact_bp.route('/contact')
def contact_page():
    if request.method == 'POST':
        # do contact form stuff here
        pass # do nothing
    try:
        return render_template('contact.html')
    except TemplateNotFound: 
        abort(404)