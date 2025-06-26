# User model for the database

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime, timezone
import os
from cryptography.fernet import Fernet
import hashlib

# Hash passwords (w/ salt)
# Objectives:
# 1) Make sure no plaintext passwords are stored.
# 2) Security is top priority.
# Using Scrypt algorithm via werkzeug.security.generate_password_hash() as it is intentionally slower and considered modern/secure.

# Encrypt+hash emails.
# Objectives: 
# 1) Make sure no plaintext emails are stored.
# 2) Make sure that they can still be used as unique identifiers for users to allow login.
# This will allow for fast lookup and login using the hash, and then decryption can happen as needed.
# Would be able to use this for password reset functionality as well.

# fernet used for symmetric encryption of emails using a secret key. KEEP THIS KEY SAFE.
# hashlib's SHA-256 used for deterministic (same input -> same output), fast, unsalted hashing of emails.

def get_fernet():
    key = os.environ.get('EMAIL_ENCRYPTION_KEY')
    if not key:
        raise RuntimeError("EMAIL_ENCRYPTION_KEY is not set in environment variables.")
    return Fernet(key.encode())

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True) # auto increments by default
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email_hash = db.Column(db.String(200), unique=True, nullable=False)
    email_encrypted = db.Column(db.LargeBinary, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    is_active_flag = db.Column(db.Boolean, nullable=False, default=True) # accounts are set as active by default.
    employee_id = db.Column(db.Integer, nullable=True, autoincrement=True) # employee_id imported from csv. Needs to be unique, but allow null for guests.

   
    # hash email function is static because it does not need to be tied to a specific user instance.
    # using SHA-256 because it is deterministic. Not adding salt
    @staticmethod
    def hash_email(email):
        # normalize by removing whitespace and setting to lowercase
        normalized_email = email.strip().lower()
        # hash using SHA-256
        email_hash = hashlib.sha256(normalized_email.encode()).hexdigest()
        return email_hash

    def set_email(self, email):
        normalized_email = email.strip().lower()
        self.email_hash = self.hash_email(normalized_email)
        self.email_encrypted = get_fernet().encrypt(normalized_email.encode())

    def get_email(self):
        return get_fernet().decrypt(self.email_encrypted).decode()
    
    def set_role(self, role):
        self.role = role.strip().lower()

    def get_role(self):
        return self.role
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt', salt_length=16)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        # flask-login has this as True by default for logged in users,
        # but any add'l logic can go here to define the baseline for what is considered authenticated
        return True

    def is_active(self):
        return self.is_active_flag
    
    # return string representation of user. This would be the hashed email.
    def __repr__(self):
        return f'<User {self.email_hash}>'