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
    # MFA expires after 10 minutes
    mfa_status = session.get("mfa_authenticated")
    mfa_time_last_auth = session.get("mfa_authenticated_at")

    if mfa_status == True and mfa_time_last_auth:
        mfa_time_last_auth = datetime.fromisoformat(mfa_time_last_auth)
        if datetime.now(timezone.utc) - mfa_time_last_auth < timedelta(minutes=10):
            return render_template("admins-only.html")
    
    # If above check fails, redirect to mfa page for reauth
    return redirect(url_for("auth.mfa_reauth", next=request.url))


#TODO: Consider adding a go to page feature?
#TODO: Styling so that the table looks nicer?
# audit log route that displays table of auth events. Uses same admins-only access logic as above
@admin_bp.route("/audit-log")
@login_required
def audit_log():
    # Enforce RBAC here.
    # log event if user is not authorized
    if not hasattr(current_user, "role") or current_user.role != "admin":
        log_auth_event("user_denied_access", user_id=current_user.id, details="User attempted to access admin-only page with insufficient permissions.")
        abort(403)  # Forbidden: Not authorized

    # pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 8

    # sorting setup
    sort = request.args.get("sort", "timestamp")
    direction = request.args.get("direction", "desc")

    sort_options = {
        "user_id": AuthEvent.user_id,
        "event_type": AuthEvent.event_type,
        "timestamp": AuthEvent.timestamp,
        "ip_address": AuthEvent.ip,
        "user_agent": AuthEvent.user_agent,
        "details": AuthEvent.details
    }
    sort_column = sort_options.get(sort, AuthEvent.timestamp)
    if direction == "asc":
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()

    # query events, sort by newest first by default
    pagination = pagination = AuthEvent.query.order_by(sort_column).paginate(page=page, per_page=per_page, error_out=False)
    audit_events = pagination.items

    # convert to local time. Python has been handling timezone aware timestamps,
    # but MySQL's DateTime does not store the timezone information.
    # Since DateTime is naive, it is stored as UTC in db
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
            return render_template("audit-log.html", audit_events=audit_events, pagination=pagination, page=page, sort=sort, direction=direction)
    
    # If above check fails, redirect to mfa page for reauth
    return redirect(url_for("auth.mfa_reauth", next=request.url))
