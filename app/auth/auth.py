import functools
from flask import Blueprint, redirect, render_template, request, session, url_for, abort, flash
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from flask_login import login_user, logout_user, login_required
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from app import db, limiter
from app.auth.forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    try:
        next_page = request.args.get('next')
        form = LoginForm()
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
        return render_template('login.html', form=form)
    except TemplateNotFound:
        abort(404)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

# prevent attacks that redirect to external sites
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc