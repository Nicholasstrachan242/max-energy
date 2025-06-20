import functools, logging
from flask import Blueprint, redirect, render_template, request, session, url_for, abort, flash
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from app import db, limiter
from app.auth.forms import LoginForm, ChangePasswordForm


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
# log in user
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    try:
        next_page = request.args.get('next')
        form = LoginForm()
        error = None
        if request.method == 'POST':
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email_hash=User.hash_email(email)).first()
            if user and user.check_password(password):
                login_user(user, remember=False)
                user.last_login = datetime.now(timezone.utc)
                from app import db
                db.session.commit()
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for('dashboard.dashboard_page'))
            else:
                # error message
                error = 'Invalid email or password'
        return render_template('login.html', form=form, error=error)
    except TemplateNotFound:
        abort(404)

# log out user
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

# Change password - Only allowed for logged in users and using existing password
# error messages displayed when staying on same page
# flash message displayed after successful change and redirect
@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    error = None
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            error = 'Current password is incorrect.'
        elif form.new_password.data == form.current_password.data:
            error = 'New password must be different from current password.'
        else:
            current_user.set_password(form.new_password.data)
            from app import db
            db.session.commit()
            flash('Your password has been changed successfully.', 'info')
            return redirect(url_for('dashboard.dashboard_page'))
    return render_template('change-password.html', form=form, error=error)


# prevent attacks that redirect to external sites
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc