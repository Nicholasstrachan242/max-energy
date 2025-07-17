# Test core authentication functionality here

# Test 1: Test that user CANNOT log in with invalid credentials. 
# Test 2: Test that user CAN log in with valid credentials.
#   - Make sure NO information is revealed about whether or not the user exists.
# Test 3: Test that a logged in user can log out.
# Test 4: Test that a protected page redirects to login page if user is not logged in.

import pytest
from app import db
from app.models.User import User

TEST_USER_EMAIL = "testuser@test.com"
TEST_USER_PASS = "testpass"
TEST_USER_FIRST = "Test"
TEST_USER_LAST = "User"
TEST_USER_ROLE = "employee"

@pytest.fixture
def test_user():
    # check if test user exists, and if it does, delete it
    db.session.rollback()
    User.query.filter_by(email_hash=User.hash_email(TEST_USER_EMAIL)).delete()
    db.session.commit()

    # create test user
    user = User(
        first_name=TEST_USER_FIRST,
        last_name=TEST_USER_LAST,
        role=TEST_USER_ROLE,
    )
    user.set_email(TEST_USER_EMAIL)
    user.set_password(TEST_USER_PASS)
    db.session.add(user)
    db.session.commit()
    yield user
    
    # cleanup - delete test user
    User.query.filter_by(email_hash=User.hash_email(TEST_USER_EMAIL)).delete()
    db.session.commit

def login(client, email, password):
    return client.post("/auth/login",
                       data={"email": email, 
                             "password": password, 
                        },
                       follow_redirects=True
                    )

def logout(client):
    return client.get("/auth/logout", follow_redirects=True)

# Test 1: Test that user CANNOT log in with invalid credentials.
def test_login_bad_credentials(app, client, test_user):
    response = login(client, TEST_USER_EMAIL, "iforgotmypassword")
    assert b"invalid email or password" in response.data.lower()

# Test 2: Test that user can log in with valid credentials.
def test_login_valid_credentials(app, client, test_user):
    response = login(client, TEST_USER_EMAIL, TEST_USER_PASS)
    assert b"dashboard" in response.data.lower()

# Test 3: Test that a logged in user can log out.
def test_logout(app, client, test_user):
    login(client, TEST_USER_EMAIL, TEST_USER_PASS)
    response = logout(client)
    assert b"log in" in response.data.lower() or b"login" in response.data.lower()

# Test 4: Test that a protected page redirects to login page if user is not logged in.
def test_protected_page_redirect(client):
    response = client.get("/dashboard", follow_redirects=True)
    assert b"log in" in response.data.lower() or b"login" in response.data.lower()
