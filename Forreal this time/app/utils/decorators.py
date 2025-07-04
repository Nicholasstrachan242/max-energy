# This file should only contain decorators, not route definitions.
# All route functions should be in their respective blueprint files.

from functools import wraps
from flask import session, redirect, url_for, flash
from db import User

def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Please log in first.')
                return redirect(url_for('auth.login'))
            user = User.query.filter_by(username=session['username']).first()
            if not user or permission_name not in [perm.name for perm in user.role.permissions]:
                flash('Access denied. You do not have the required permission.')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
