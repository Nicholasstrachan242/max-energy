from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='scrypt', salt_length=16)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # return string representation of user.
    def __repr__(self):
        return f'<User {self.email}>'