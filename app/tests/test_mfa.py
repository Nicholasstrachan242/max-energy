# Test Multifactor authentication logic here.

# Test	What to test		        Details
# 1		Secret generation			Secret generation. 32 char, base32
# 2     Secret encryption           use Fernet encryption for base32 secret
# 3		TOTP core functionality		TOTP (Time based OTP) code generation and verification
# 4	    QR code generation			QR code in plaintext, and then in image form
# 5		MFA setup flow?				User-facing MFA setup and confirmation
# 6		Login with MFA				Create test user to log in with MFA, then delete test user
# 7		Disabling MFA				Create user, enable MFA, then disable MFA and delete test user

# Tests w/ logic were written here to get a grasp on pyotp syntax and functionality. 

import pytest
import pyotp
import time
from app import db
from app.models.User import User
from app.auth import mfa
from cryptography.fernet import Fernet


TEST_USER_EMAIL = 'testuser@test.com'
TEST_USER_PASS = 'testpass'
TEST_USER_FIRST = 'Test'
TEST_USER_LAST = 'User'
TEST_USER_ROLE = 'employee'

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


# Test 1: Generate a 32-character base32 secret for authenticator apps, then encrypt and decrypt it
def test_generate_secret():
    secret = mfa.generate_base32_secret()
    assert isinstance(secret, str) # check if string
    assert len(secret) == 32 # check if 32 chars

# Test 2: Test encryption and decryption of secret using fernet
def test_encrypt_decrypt_secret():
    # generate encryption key and secret
    key = Fernet.generate_key()
    fernet = Fernet(key)
    secret = mfa.generate_base32_secret()
    # encrypt
    encrypted_secret = mfa.encrypt_secret(secret, key)
    # decrypt
    decrypted_secret = mfa.decrypt_secret(encrypted_secret, key)
    # make sure original secret matches secret passed through encrpyt+decrypt
    assert secret == decrypted_secret

# Test 3: Test Time-based OTP generation and verification
def test_totp():
    # setup totp
    secret = mfa.generate_base32_secret()
    totp = mfa.generate_totp(secret)

    # set fixed time so that waiting in real time is not necessary
    test_time = 1751587200 # timestamp for July 4th, 2025
    # generate otp. By default should be a 6 digit numeric string
    otp = totp.at(test_time) 

    # otp should successfully verify at exactly the test time
    assert mfa.verify_totp(totp, otp, for_time=test_time) is True

    # otp should NOT verify after 30 seconds have passed
    assert mfa.verify_totp(totp, otp, for_time=test_time + 30) is False

    # otp should NOT verify an incorrect code even at test time
    assert mfa.verify_totp(totp, "123456", for_time=test_time) is False

# Test 4: Generate QR code - plaintext
def test_generate_qr_code_plaintext():
    # generate secret
    secret = mfa.generate_base32_secret()
    # Create TOTP
    totp = mfa.generate_totp(secret)
    # generate provisioning uri
    uri = totp.provisioning_uri(name=TEST_USER_EMAIL, issuer_name="Test App")

    # assert that uri is the correct format
    assert uri.startswith("otpauth://totp/")

# Test 5: Test the core of the MFA functionality
# Create test user, enable mfa, store the encrypted secret, and then allow them to log in using their otp.
def test_mfa_user_setup(app, test_user):
    # set up totp and provisioning uri
    secret = mfa.generate_base32_secret()
    totp = mfa.generate_totp(secret)
    uri = totp.provisioning_uri(name=TEST_USER_EMAIL, issuer_name="Test App")

    # encrypt and store secret. Toggle mfa_enabled to True.
    key = Fernet.generate_key() # in prod, there should be one consistent key
    encrypted_secret = mfa.encrypt_secret(secret, key)
    test_user.mfa_secret = encrypted_secret
    test_user.mfa_enabled = True
    db.session.commit()

    # allow test user to log in using their otp
    decrypted_secret = mfa.decrypt_secret(test_user.mfa_secret, key)
    totp = mfa.generate_totp(decrypted_secret)
    otp = totp.now() # this would be when the user puts in their otp

    assert totp.verify(otp)