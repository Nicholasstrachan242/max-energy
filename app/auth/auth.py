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
from app.auth.auth_logging import log_auth_event
from flask_login import LoginManager

# auth.py handles all authentication events that occur within the app.

# initialize and set up login manager
login_manager = LoginManager()

def init_login_manager(app):
    login_manager.init_app(app)

    # set login view
    login_manager.login_view = 'auth.login'

    # handle login messages for pages that require login
    login_manager.login_message = "Please log in to view this page."
    login_manager.login_message_category = "warning"

    # helper functions
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.User import User
        return User.query.get(int(user_id))
    
    # handle unauthorized/unauthenticated access
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        log_auth_event("unauthorized_access", details=f"Unauthenticated user attempted to access: {request.path}")
        return redirect(url_for('auth.login', next=request.path))


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
                # log user in + log event
                login_user(user, remember=False)
                user.last_login = datetime.now(timezone.utc)
                log_auth_event("login", user_id=user.id)
                from app import db
                db.session.commit()
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for('dashboard.dashboard_page'))
            else:
                # error message + log event
                error = 'Invalid email or password'
                log_auth_event("failed_login", details=f"Invalid email or password. Attempted email hash: {User.hash_email(email)}")
        return render_template('login.html', form=form, error=error)
    except TemplateNotFound:
        abort(404)

# log out user + log event
@auth_bp.route('/logout')
@login_required
def logout():
    log_auth_event("logout", user_id=current_user.id)
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
        if not current_user.check_password(form.current_password.data): # log event if wrong password is used to attempt change
            error = 'Current password is incorrect.'
            log_auth_event("failed_password_change", user_id=current_user.id, details=f"Attempt to change password failed due to using incorrect current password.")
        elif form.new_password.data == form.current_password.data:
            error = 'New password must be different from current password.'
        else: # success + log event
            current_user.set_password(form.new_password.data)
            from app import db
            db.session.commit()
            log_auth_event("password_change", user_id=current_user.id)
            flash('Your password has been changed successfully.', 'info')
            return redirect(url_for('dashboard.dashboard_page'))
    return render_template('change-password.html', form=form, error=error)


# prevent attacks that redirect to external sites
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc