from app import create_app
from app import db

# entry point for flask app. Pass app.run:app if using waitress-serve. 
app = create_app()

with app.app_context():
    from app.models import User
    db.create_all()

if __name__ == '__main__':
    app.run()