from app import db

class Names(db.Model):
    __tablename__ = 'names'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Names id={self.id} firstname={self.firstname} lastname={self.lastname}>"