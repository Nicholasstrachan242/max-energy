import functools, logging, os
from flask import Blueprint, redirect, render_template, request, url_for, abort, flash, session
from jinja2 import TemplateNotFound
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from app import db, limiter
from app.auth.forms import LoginForm, ChangePasswordForm, MfaLoginForm
from app.auth.auth_logging import log_auth_event
from app.auth import mfa
from flask_login import LoginManager

# auth.py handles general login/logout authentication events and restricted routes within the app.

# initialize and set up login manager
login_manager = LoginManager()

def init_login_manager(app):
    login_manager.init_app(app)

    # set login view
    login_manager.login_view = "auth.login"

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
        flash(login_manager.login_message, login_manager.login_message_category)
        log_auth_event("unauthorized_access", details=f"Unauthenticated user attempted to access: {request.path}")
        return redirect(url_for("auth.login", next=request.path))

# create blueprint, set prefix. All routes here are to begin with /auth
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# log in user
@auth_bp.route("/login", methods=["GET", "POST"])
# login rate limiting
# by default, this limits by IP address
# 10 attempts per 60 second window. After exceeding, the user has to wait until 60s AFTER the first attempt
@limiter.limit("10 per minute",
               deduct_when=lambda response: (
                   # only count failed, submitted login attempts towards this limit
                   request.method == "POST" and response.status_code == 200
               ))
def login():
    try:
        next_page = request.args.get("next")
        form = LoginForm()
        error = None
        if request.method == "POST":
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email_hash=User.hash_email(email)).first()
            if user and user.check_password(password):
                # make sure account is active. Otherwise, deny access and log the event.
                if not user.is_active():
                    error = "Your account has been deactivated. Please contact IT support."
                    log_auth_event("deactivated_login_attempt", user_id=user.id)
                    return render_template("login.html", form=form, error=error)
                # check for MFA
                if user.mfa_enabled:
                    #store user id in session, but do not log in yet
                    session["mfa_user_id"] = user.id
                    next_page = request.args.get("next")
                    if next_page:
                        return redirect(url_for("auth.mfa_login", next=next_page))
                    else:
                        return redirect(url_for("auth.mfa_login"))

                # if MFA is not enabled, normal login logic applies
                # log user in + log event
                login_user(user, remember=False)
                user.last_login = datetime.now(timezone.utc)
                log_auth_event("login", user_id=user.id)
                from app import db
                db.session.commit()
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for("dashboard.dashboard_page"))
            else:
                # error message + log event
                error = "Invalid email or password"
                log_auth_event("failed_login", details=f"Invalid email or password. Attempted email hash: {User.hash_email(email)}")
        return render_template("login.html", form=form, error=error)
    except TemplateNotFound:
        abort(404)

# handle MFA. If user has mfa enabled, then after submitting email and password, they must submit a valid OTP on this route.
# By default, OTP is valid for 30s
@auth_bp.route("/mfa", methods=["GET","POST"])
def mfa_login():
    form = MfaLoginForm()
    error = None

    # check for user session. Only stay on the mfa page if the session exists from a successful email and password submission
    user_id = session.get("mfa_user_id")
    if not user_id:
        # No pending MFA, redirect to login
        flash("Please log in to continue.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    # Check if user exists, if they have mfa enabled, and if they have an mfa secret in the db
    if not user or not user.mfa_enabled or not user.mfa_secret:
        # clear session
        session.pop("mfa_user_id", None)
        flash("Unable to verify user. Please log in again.", "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        otp = form.one_time_password.data.strip()
        key = os.environ["MFA_KEY"].encode()
        try:
            decrypted_secret = mfa.decrypt_secret(user.mfa_secret, key)
            totp = mfa.generate_totp(decrypted_secret)
            # if OTP is valid, complete login
            if mfa.verify_totp(totp, otp):
                login_user(user, remember=False)
                user.last_login = datetime.now(timezone.utc)
                log_auth_event("login", user_id=user.id)
                db.session.commit()
                session.pop("mfa_user_id", None)
                next_page = request.args.get("next")
                if next_page and is_safe_url(next_page):
                    return redirect(next_page)
                return redirect(url_for("dashboard.dashboard_page"))
            else:
                error = "Invalid code. Please try again."
                log_auth_event("failed_mfa", user_id=user.id, details="Invalid OTP entered.")
        except Exception as e:
            error = "An error occurred during MFA verification."
            log_auth_event("failed_mfa", user_id=user.id, details=str(e))

    return render_template("mfa-login.html", form=form, error=error)

# log out user + log event
@auth_bp.route("/logout")
@login_required
def logout():
    log_auth_event("logout", user_id=current_user.id)
    logout_user()
    session.clear() # Delete all session data on logout
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))

# Change password - Only allowed for logged in users and using existing password
# error messages displayed when staying on same page
# flash message displayed after successful change and redirect
@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    error = None
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data): # log event if wrong password is used to attempt change
            error = "Current password is incorrect."
            log_auth_event("failed_password_change", user_id=current_user.id, details=f"Attempt to change password failed due to using incorrect current password.")
        elif form.new_password.data == form.current_password.data:
            error = "New password must be different from current password."
        else: # success + log event
            current_user.set_password(form.new_password.data)
            from app import db
            db.session.commit()
            log_auth_event("password_change", user_id=current_user.id)
            flash("Your password has been changed successfully.", "info")
            return redirect(url_for("dashboard.dashboard_page"))
    return render_template("change-password.html", form=form, error=error)


# Set up MFA. Allow logged in user to generate a qr code and add MFA to their account.
@auth_bp.route("/mfa/setup", methods=["GET", "POST"])
@login_required
def mfa_setup():
    # check if user already has MFA setup. If so, render the template with an mfa_enabled flag
    # A QR code will not be shown to the user.
    if current_user.mfa_enabled:
        return render_template("mfa-setup.html", mfa_enabled=True)
    
    error = None

    # Generate a new secret only if there isn't already one for the session
    if "mfa_secret" not in session:
        session["mfa_secret"] = mfa.generate_base32_secret()
    secret = session["mfa_secret"]

    # setup MFA object
    totp = mfa.generate_totp(secret)
    uri = mfa.generate_uri(secret, current_user.get_email())
    
    # TODO: remove this after test
    print(f"The email {current_user.get_email()} will be shown in the authenticator app.")
    print("qrcode uri:", uri)
    print("mfa secret BEFORE verify:", session["mfa_secret"])

    qr_code_data = mfa.generate_qr_code(uri)

    if request.method == "POST":
        otp = request.form.get("otp", "").strip()

        # testing if otp and totp are in sync
        # print("mfa secret after hitting submit:", session["mfa_secret"])
        # print("Server TOTP now:", totp.now())
        # print("User submitted OTP:", otp)

        if mfa.verify_totp(totp, otp):
            # encrypt and save secret, enable MFA
            key = os.environ["MFA_KEY"].encode()
            encrypted_secret = mfa.encrypt_secret(secret, key)
            current_user.mfa_secret = encrypted_secret
            current_user.mfa_enabled = True
            db.session.commit()

            # log event
            log_auth_event("mfa_enabled", user_id=current_user.id)
            # ENSURE THAT SECRET IS REMOVED FROM SESSION AFTER USER IS FINISHED SETTING UP
            session.pop("mfa_secret", None)

            # check session. It should NOT contain mfa_secret
            # print("Session after pop:",dict(session))

            flash("Multi-factor authentication enabled successfully!", "info")
            return redirect(url_for("dashboard.dashboard_page"))
        else:
            error = "Invalid code. Please try again"

    return render_template(
        "mfa-setup.html",
        qr_code_data=qr_code_data,
        error=error,
        mfa_enabled=False
    )

# prevent attacks that redirect to external sites
# only allow relative-only urls on same domain, no absolute urls. Stricter approach used here
# prevent path traversal
def is_safe_url(target):
    # remove backslashes to prevent browser quirks
    target = target.replace("\\", "")
    # resolve target relative to the host URL
    test_url = urlparse(urljoin(request.host_url, target))
    normalized_path = os.path.normpath(test_url.path)
    return (
        test_url.scheme in ("http", "https") and
        not test_url.netloc and
        normalized_path.startswith("/") and
        # prevent traversal and escaping
        not normalized_path.startswith("/..") and
        "/../" not in normalized_path
    )
