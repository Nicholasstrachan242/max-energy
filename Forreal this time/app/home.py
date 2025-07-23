from flask import Blueprint, render_template

guest_bp = Blueprint('guest', __name__)

@guest_bp.route('/')
def home():
    return render_template('guest.home.html')

@guest_bp.route('/info')
def info():
    return render_template('guest.info.html')

@guest_bp.route('/contact')
def contact():
    return render_template('guest.contact.html') 