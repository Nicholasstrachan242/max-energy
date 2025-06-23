# Helper functions for auth event logging
# log the following types of auth events to the database:
# - login
# - failed login attempt
# - logout
# - password change
# - unauthorized/authenticated access

from app import db
from app.models import AuthEvent
from flask import request
from datetime import datetime, timezone

def log_auth_event(event_type, user_id=None, details=None): # set None as default default for optional parameters
    try:
        ip = request.remote_addr if request else None
        user_agent = request.user_agent.string if request.user_agent.string else None
        print("User-Agent string:", user_agent)
        event = AuthEvent(
            user_id=user_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            ip=ip,
            user_agent=user_agent,
            details=details
        )
        db.session.add(event)
        db.session.commit()
    except Exception as e:
        # do not crash app if log fails
        from flask import current_app
        current_app.logger.error(f"Failed to log auth event: {e}")
