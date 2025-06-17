# User model for the database

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime
from datetime import timezone

# TODO: encrypt+hash emails
# Purpose: make sure no plaintext emails are stored and that they can still be used as unique identifiers for users
# This will allow for fast lookup and login using the hash, and then decryption can happen as needed.
# Would be able to use this for password reset functionality as well.

# fernet to be used for symmetric encryption of emails using a secret key. KEEP THIS KEY SAFE.
# hashlib's SHA-256 to be used for deterministic (same input -> same output), fast, unsalted hashing of emails. 
# not using werkzeug.security.generate_password_hash() because it is not deterministic and is slower.


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True) # auto increments by default
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt', salt_length=16)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True

    # for use when adding activate/deactivate features
    def is_active(self):
        return True
    
    # return string representation of user.
    def __repr__(self):
        return f'<User {self.email}>'