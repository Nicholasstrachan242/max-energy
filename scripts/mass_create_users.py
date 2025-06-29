import os, sys, re
from datetime import datetime
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script can create multiple users at once. It will skip duplicates and enforce password requirements.

# run script as module: python -m scripts.<script_name> (without .py extension)

# Add the project root directory to Python path
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, project_root)

from app import create_app, db
from app.models.User import User

# List of dicts of users to create
USERS_TO_CREATE = [
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@maxx-energy.com",
        "password": "--REDACTED--",
        "role": "employee",
    },
    {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@maxx-energy.com",
        "password": "--REDACTED--",
        "role": "guest",
    },
    # Add more users to this list as needed
]

# Check for the following password requirements:
# - Minimum length of 12 characters
# - At least one uppercase letter
# - At least one number
# - At least one symbol
def is_strong_password(password):
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;/`~']", password):
        return False, "Password must contain at least one symbol."
    return True, ""

def main():
    app = create_app()
    with app.app_context():
        valid_users = 0  # Counter for successfully created users
        for entry in USERS_TO_CREATE:
            # Make sure all required fields are present. Otherwise, skip the entry.
            required_fields = ["first_name", "last_name", "email", "password", "role"]
            if not all(field in entry and entry[field] for field in required_fields):
                print(f"Skipping entry (missing required fields): {entry}")
                continue

            # Only allow these roles in this script: manager, employee, guest
            role = entry["role"].strip().lower()
            if role not in ["manager", "employee", "guest"]:
                print(f"Skipping {entry['email']}: Invalid role '{role}'. Only manager, employee, and guest roles are allowed.")
                continue

            # Check if user already exists. If so, skip to prevent duplicates.
            email = entry["email"].strip().lower()
            if User.query.filter_by(email_hash=User.hash_email(email)).first():
                print(f"Skipping: {email} already exists.")
                continue

            password = entry["password"]
            valid, msg = is_strong_password(password)
            if not valid:
                print(f"Skipping {email}: {msg}")
                continue

            user = User(
                first_name=entry["first_name"],
                last_name=entry["last_name"],
                role=entry["role"]
            )
            # uses fernet encrpytion + SHA-256 hashing on email
            # uses scrypt hashing on password
            user.set_email(email)
            user.set_password(password)
            db.session.add(user)
            print(f"User {email} ready to be added to db.")
            valid_users += 1  # Increment counter for each valid user

        try:
            db.session.commit()

            print(f"All valid users have been created successfully. Total created: {valid_users}")
            # log the event
            log_auth_event("users_created", details=f"{valid_users} user(s) created via multiple create script.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding users to database: {e}")
            sys.exit(1)
    
if __name__ == "__main__":
    main()