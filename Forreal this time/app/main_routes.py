from flask import Blueprint, render_template, session, redirect, url_for, flash
from db import db, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=session['username']).first()
    allowed_roles = ['admin', 'executive', 'manager', 'staff']
    if user.role.name in allowed_roles:
        session['role'] = user.role.name
        user_permissions = [perm.name for perm in user.role.permissions]
        # Pass user and role to the template
        return render_template('dashboard.html', user=user, user_permissions=user_permissions)
    else:
        flash('Access denied.')
        return redirect(url_for('main.home'))

@main_bp.route('/home')
def home():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.role.name == 'guest':
            session['role'] = user.role.name
            return render_template('guest.home.html')
        else:
            return redirect(url_for('main.dashboard'))
    return render_template('guest.home.html')

@main_bp.route('/role-management')
def role_management_redirect():
    return redirect(url_for('admin.role_management'))