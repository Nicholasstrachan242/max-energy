# Helper functions for auth event logging
# log the following types of auth events to the database:
# - login
# - failed login attempt
# - logout
# - password change
# - unauthorized/authenticated access

from app import db
from app.models import AuthEvent
from flask import request, has_request_context
from datetime import datetime, timezone
import os, logging
import time

# setup logger for auth events
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs') # set directory to logs folder in project root
os.makedirs(log_dir, exist_ok=True)
logging.Formatter.converter = time.gmtime # use UTC for timestameps
log_file = os.path.join(log_dir, 'auth_events.log')
auth_logger = logging.getLogger('auth_events')
auth_logger.setLevel(logging.INFO)

if not auth_logger.handlers:
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    auth_logger.addHandler(file_handler)


# log auth event to db and to file
def log_auth_event(event_type, user_id=None, details=None):
    try:
        if has_request_context():
            ip = request.remote_addr
            user_agent = request.user_agent.string if request.user_agent.string else None
        else:
            ip = None
            user_agent = None

        event = AuthEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc),
            ip=ip,
            user_agent=user_agent,
            details=details
        )
        # log to file as backup
        auth_logger.info(
            f"event_type={event_type}, user_id={user_id}, ip={ip}, user_agent={user_agent}, details={details}"
        )

        db.session.add(event)
        db.session.commit()

    except Exception as e:
        # do not crash app if log fails
        try:
            from flask import current_app
            if has_request_context():
                current_app.logger.error(f"Failed to log auth event: {e}")
            else:
                auth_logger.error(f"Failed to log auth event. No request context: {e}")
        except Exception:
            # if loggers don't work
            print(f"Logger was not able to handle exception. Failed to log auth event: {e}")


