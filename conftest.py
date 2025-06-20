import os
import sys
import pytest
from app import create_app, db

# Get absolute path of project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Add project root directory to the Python path
sys.path.insert(0, project_root)

@pytest.fixture(scope='session')
def app():
    app = create_app({'TESTING': True})
    with app.app_context():
        db.create_all()  # Make sure schema exists for all tests
        yield app
        # Do not drop tables after tests

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

# Always rollback the session after each test to avoid session state errors
@pytest.fixture(autouse=True)
def cleanup_db_session():
    yield
    db.session.rollback()