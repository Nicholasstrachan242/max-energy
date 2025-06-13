# Test the welcome page with local test database.
# Use same schema as actual production database for Users.

# Test 1: Check that welcome page requires login
# Test 2: Check that welcome page works with authentication

import pytest
import os
from dotenv import load_dotenv
from flask import Flask, url_for
from app import create_app, db
from app.models.User import User
from flask_login import login_user

# load environment variables
load_dotenv()

@pytest.fixture
def app():
    app = create_app()
    db_uri = (
        f"mysql+pymysql://{os.getenv('TEST_DB_USER')}:{os.getenv('TEST_DB_PASS')}"
        f"@{os.getenv('TEST_DB_HOST')}:{os.getenv('TEST_DB_PORT')}/{os.getenv('TEST_DB_NAME')}"
    )

    # show uri
    print(f"\nAttempting to connect with: {db_uri}")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

# Create session for each test. Flask-SQLAlchemy automatically sets up engine and scoped session.
@pytest.fixture(autouse=True)
def session(app):
    with app.app_context():
        # Start a transaction
        db.session.begin()
        
        yield db.session
        
        db.session.rollback()
        db.session.remove()

# Create test user.
@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test User',
            role='staff'
        )
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        return user

# Create test client for authentication
@pytest.fixture
def auth_client(app, client, test_user):
    with app.app_context():
        with client.session_transaction() as session:
            # Log in as test user
            session['_user_id'] = str(test_user.id)
    return client

# Test 1: Check that welcome page requires login

# Test 2: Check that welcome page works with authentication

