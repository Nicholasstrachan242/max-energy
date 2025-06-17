# admin.py is meant to show a restricted access (admins-only.html) page for admins only.
# It is meant to demonstrate RBAC (Role-Based Access Control) and the route will only be accessible to admins.

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/admins-only')
@login_required # require login.
def admins_only():
    # Enforce RBAC here.
    if not hasattr(current_user, "role") or current_user.role != 'admin':
        abort(403)  # Forbidden: Not authorized
    return render_template('admins-only.html', user=current_user)