# admin.py is meant to show a restricted access (admins-only.html) page for admins only.
# It is meant to demonstrate RBAC (Role-Based Access Control) and the route will only be accessible to admins.

from flask import Blueprint, render_template, abort, session, redirect, url_for, request
from flask_login import login_required, current_user
from app.auth.auth_logging import log_auth_event
from app.models.AuthEvent import AuthEvent
from datetime import datetime, timezone, timedelta

admin_bp = Blueprint("admin", __name__, url_prefix='/admin')

# admin control panel route
@admin_bp.route("/admins-only")
@login_required # require login.
def admins_only():
    # Enforce RBAC here.
    # log event if user is not authorized
    if not hasattr(current_user, "role") or current_user.role != "admin":
        log_auth_event("user_denied_access", user_id=current_user.id, details="User attempted to access admin-only page with insufficient permissions.")
        abort(403)  # Forbidden: Not authorized

    # Check for MFA status and timeout
    # admin must re-authenticate with OTP if MFA is expired
    # MFA expires after 5 minutes
    mfa_status = session.get("mfa_authenticated")
    mfa_time_last_auth = session.get("mfa_authenticated_at")

    if mfa_status == True and mfa_time_last_auth:
        mfa_time_last_auth = datetime.fromisoformat(mfa_time_last_auth)
        if datetime.now(timezone.utc) - mfa_time_last_auth < timedelta(minutes=5):
            return render_template("admins-only.html")
    
    # If above check fails, redirect to mfa page for reauth
    return redirect(url_for("auth.mfa_reauth", next=request.url))

# audit log route. Uses same admins-only access logic as above
@admin_bp.route("/audit-log")
@login_required
def audit_log():
    # Enforce RBAC here.
    # log event if user is not authorized
    if not hasattr(current_user, "role") or current_user.role != "admin":
        log_auth_event("user_denied_access", user_id=current_user.id, details="User attempted to access admin-only page with insufficient permissions.")
        abort(403)  # Forbidden: Not authorized

    # get all auth events, sort by newest first
    audit_events = AuthEvent.query.order_by(AuthEvent.timestamp.desc()).all()
    # convert to local time. Python has been handling timezone aware timestamps,
    # but MySQL's DateTime does not store the timezone information.
    # Since DateTime is naive, it is stored as UTC
    for event in audit_events:
        if event.timestamp and event.timestamp.tzinfo is None:
            event.timestamp = event.timestamp.replace(tzinfo=timezone.utc)

    # Check for MFA status and timeout
    # admin must re-authenticate with OTP if MFA is expired
    # MFA expires after 10 minutes
    mfa_status = session.get("mfa_authenticated")
    mfa_time_last_auth = session.get("mfa_authenticated_at")

    if mfa_status == True and mfa_time_last_auth:
        mfa_time_last_auth = datetime.fromisoformat(mfa_time_last_auth)
        if datetime.now(timezone.utc) - mfa_time_last_auth < timedelta(minutes=10):
            return render_template("audit-log.html")
    
    # If above check fails, redirect to mfa page for reauth
    return redirect(url_for("auth.mfa_reauth", next=request.url))
