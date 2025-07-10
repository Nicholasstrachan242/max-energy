# Test Multifactor authentication logic here.

# Test	What to test		        What to implement
# 1		Secret generation			Secret generation function
# 2		TOTP code generation		TOTP code generation function
# 3		TOTP code verification		TOTP code verification function
# 4		QR code generation			QR code image generation function
# 5		MFA setup flow?				User-facing MFA setup and confirmation
# 6		Login with MFA				Login logic with MFA check
# 7		Disabling MFA				Logic to disable MFA for a user

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

def test_encrypt_decrypt_secret():
    # generate encryption key
    key = Fernet.generate_key()
    fernet = Fernet(key)
    
    # encrypt
    secret = pyotp.random_base32()
    encrypted_secret = fernet.encrypt(secret.encode())

    # decrypt
    decrypted_secret = fernet.decrypt(encrypted_secret).decode()

    assert secret == decrypted_secret

