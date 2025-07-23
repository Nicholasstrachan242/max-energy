# admin.py is meant to show a restricted access (admins-only.html) page for admins only.
# It is meant to demonstrate RBAC (Role-Based Access Control) and the route will only be accessible to admins.

from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from app.auth.auth_logging import log_auth_event
from app.rbac.models import RBACUser

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/admins-only')
@login_required # require login.
def admins_only():
    # Enforce RBAC here using the RBAC system
    # Check if user exists in RBAC system and has admin role
    rbac_user = RBACUser.query.filter_by(username=current_user.username).first()
    
    if not rbac_user or rbac_user.role.name != 'admin':
        log_auth_event("user_denied_access", user_id=current_user.id, details="User attempted to access admin-only page with insufficient permissions.")
        abort(403)  # Forbidden: Not authorized
    
    return render_template('admins-only.html', user=current_user)

@admin_bp.route('/rbac-access')
@login_required
def rbac_access():
    """Redirect to RBAC system if user has appropriate permissions"""
    rbac_user = RBACUser.query.filter_by(username=current_user.username).first()
    
    if not rbac_user:
        log_auth_event("user_denied_access", user_id=current_user.id, details="User not found in RBAC system.")
        abort(403)
    
    # Check if user has dashboard access permission
    has_dashboard_access = any(perm.name == 'dashboard_access' for perm in rbac_user.role.permissions)
    
    if not has_dashboard_access:
        log_auth_event("user_denied_access", user_id=current_user.id, details="User attempted to access RBAC system without dashboard_access permission.")
        abort(403)
    
    return redirect(url_for('rbac.dashboard'))