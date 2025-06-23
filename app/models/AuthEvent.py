from app import db
from datetime import datetime, timezone

# Model for logging auth events.
# Auth events may eventually be accessible via API depending on the needs of this project.

class AuthEvent(db.Model):
    __tablename__= 'auth_events'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True) # allow this to be null in case no user is tied to the event
    event_type = db.Column(db.String(50), nullable=False) # examples of event types: login, login attempt, logout, password change
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ip = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(250), nullable=True) # browser/client User-Agent string, helps identify device or browser used
    details = db.Column(db.String(500), nullable=True) # optional, any add'l details go here

