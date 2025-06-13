# Test authentication functionality here with local test database

# Test 1: Test that user CANNOT log in with invalid credentials. 
# Test 2: Test that user CAN log in with valid credentials.
# Make sure NO information is revealed about whether or not the user exists.
# Test 3: Test that a logged in user can log out.
# Test 4: Test that a protected page redirects to login page if user is not logged in.

import pytest
from app import create_app,db
from app.models.User import User

TEST_USER_EMAIL='testuser@test.com'
TEST_USER_PASS='testpass'
TEST_USER_FIRST='Test'
TEST_USER_LAST='User'
TEST_USER_ROLE='staff'

@pytest.fixture
def app():
    app=create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False # disable CSRF protection for testing
    })
    with app.app_context():
        db.create_all()
        # make sure test user exists before tests
        user = User.query.filter_by(email='test@test.com').first()
        if not user:
            user = User(
                first_name=TEST_USER_FIRST,
                last_name=TEST_USER_LAST,
                email=TEST_USER_EMAIL,
                role=TEST_USER_ROLE
            )
            user.set_password(TEST_USER_PASS)
            db.session.add(user)
            db.session.commit()

        yield app

        # cleanup after tests
        user = User.query.filter_by(email=TEST_USER_EMAIL).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, email, password):
    return client.post("/auth/login",
                       data={"email": email, "password": password}, 
                       follow_redirects=True
                    )

def logout(client):
    return client.get("/auth/logout", follow_redirects=True)

# Test 1: Test that user CANNOT log in with invalid credentials.
def test_login_bad_credentials(client):
    response = login(client, TEST_USER_EMAIL, "iforgotmypassword")
    # should stay on login page and show error message
    assert b"invalid email or password" in response.data.lower()

# Test 2: Test that user can log in with valid credentials.
def test_login_valid_credentials(client):
    response = login(client, TEST_USER_EMAIL, TEST_USER_PASS)
    # should redirect to welcome page upon successful login
    assert b"welcome" in response.data.lower()

# Test 3: Test that a logged in user can log out.
def test_logout(client):
    login(client, TEST_USER_EMAIL, TEST_USER_PASS)
    response = logout(client)
    # should redirect to login page
    assert b"log in" in response.data.lower() or b"login" in response.data.lower()

# Test 4: Test that a protected page redirects to login page if user is not logged in.
def test_protected_page_redirect(client):
    response = client.get("/welcome", follow_redirects=True)
    # should redirect to login page
    assert b"log in" in response.data.lower() or b"login" in response.data.lower()
