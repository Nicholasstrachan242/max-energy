from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email_encrypted = db.Column(db.LargeBinary, nullable=False)
    encryption_iv = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>' 