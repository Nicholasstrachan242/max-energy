# Test authentication functionality here with local test database

# Test 1: Test that user can log in with valid credentials.
# Test 2: Test that user CANNOT log in with invalid credentials.
# Make sure NO information is revealed about whether or not the user exists.
# Test 3: Test that a logged in user can log out.
# Test 4: Test that a protected page redirects to login page if user is not logged in.

import pytest
import os
from flask import Flask
from dotenv import load_dotenv
from app import create_app,db
from app.models.User import User

@pytest.fixture
def app():
    app=create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False # disable CSRF protection for testing
    })
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


