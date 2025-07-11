# ALL MFA logic goes here

import pyotp
from cryptography.fernet import Fernet


# generate secret for TOTP - 32 char, base32
def generate_base32_secret(length=32):
    return pyotp.random_base32(length=length)

# use fernet encryption for secret
def encrypt_secret(secret, key):
    fernet = Fernet(key)
    return fernet.encrypt(secret.encode())

def decrypt_secret(encrypted_secret, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_secret).decode()

# generate Time based One Time Password using secret
def generate_totp(secret):
    return pyotp.TOTP(secret)

# verify totp at provided time. By defualt, otp is valid for 30s
def verify_totp(totp, otp, for_time=None):
    return totp.verify(otp, for_time=for_time)