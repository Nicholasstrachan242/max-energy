from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

# Password hashing helpers

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)

# Encryption helpers

def generate_key():
    return Fernet.generate_key()

def encrypt_data(key, data):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(data.encode('utf-8'))

def decrypt_data(key, token):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(token).decode('utf-8') 