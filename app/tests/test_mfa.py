# Test Multifactor authentication logic here.

# Test	What to test		        What to implement
# 1		Secret generation			Secret generation. 32 char, base32
# 2     Secret encryption           Fernet encryption for base32 secret
# 3		TOTP core functionality		TOTP (Time based OTP) code generation and verification
# 4	    QR code generation			QR code image generation
# 5		MFA setup flow?				User-facing MFA setup and confirmation
# 6		Login with MFA				Login logic with MFA check
# 7		Disabling MFA				Logic to disable MFA for a user

# Tests w/ logic were written here to get a grasp on pyotp syntax and functionality. 
# TODO: Move the logic from the functions below into mfa.py and just call them here for the tests

import pytest
import pyotp
import time
from app import db
from app.models.User import User
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Test 1: Generate a 32-character base32 secret for authenticator apps, then encrypt and decrypt it
def test_generate_secret():
    secret = pyotp.random_base32()
    assert isinstance(secret, str) # check if string
    assert len(secret) == 32 # check if 32 chars

# Test 2: Test encryption and decryption of secret using fernet
def test_encrypt_decrypt_secret():
    # generate encryption key
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    # encrypt
    secret = pyotp.random_base32()
    encrypted_secret = fernet.encrypt(secret.encode())
    # decrypt
    decrypted_secret = fernet.decrypt(encrypted_secret).decode()

    # make sure original secret matches secret passed through encrpyt+decrypt
    assert secret == decrypted_secret

# Test 3: Test Time-based OTP generation and verification
def test_totp():
    # setup totp
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)

    # set fixed time so that waiting in real time is not necessary
    test_time = 1751587200 # timestamp for July 4th, 2025
    # generate otp. By default should be a 6 digit numeric string
    otp = totp.at(test_time) 

    # otp should successfully verify at exactly the test time
    assert totp.verify(otp, for_time=test_time) is True

    # otp should NOT verify after 30 seconds have passed
    assert totp.verify(otp, for_time=test_time + 30) is False

    # otp should NOT verify an incorrect code even at test time
    assert totp.verify('123456', for_time=test_time) is False