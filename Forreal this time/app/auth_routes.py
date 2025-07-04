from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from db import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            session['role'] = user.role.name
            user.last_login = datetime.utcnow()
            db.session.commit()
            if user.role.name == 'admin':
                return redirect(url_for('admin.role_management'))
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login')) 