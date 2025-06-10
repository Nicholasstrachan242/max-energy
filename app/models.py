from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwHash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)