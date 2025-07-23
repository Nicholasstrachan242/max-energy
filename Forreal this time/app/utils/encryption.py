from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String
import base64
import os

# Generate and store this key securely!
ENCRYPTION_KEY = os.environ.get('EMAIL_ENCRYPTION_KEY') or Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)

class EncryptedString(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return fernet.decrypt(value.encode()).decode()
