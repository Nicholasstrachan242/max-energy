# Multifactor Authentication logic goes here.
# using Time Based One Time Passwords
# Users will be able to set up MFA using the authenticator app of their choice. (Google, Microsoft, 2FAS, Authy, etc.)

import pyotp
from cryptography.fernet import Fernet
import qrcode
import io
import base64

# helper functions for MFA

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

# generate provisioning uri for qr code
def generate_uri(secret, email, issuer_name="Maxx Energy"):
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer_name)

# verify totp at provided time. By default, otp is valid for 30s.
# valid_window allows codes from previous and next 30s window to be accepted
def verify_totp(totp, otp, for_time=None, valid_window=1):
    return totp.verify(otp, for_time=for_time, valid_window=valid_window)

# generate QR code as base64-encoded png
def generate_qr_code(uri):
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
