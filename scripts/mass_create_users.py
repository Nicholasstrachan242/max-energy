import os
import sys
import re
from datetime import datetime
from app import create_app, db
from app.models.User import User

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script is used to create multiple users at once. It will skip duplicates and enforce password requirements.

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# List of dictionaries of users to create
USERS_TO_CREATE = [
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@maxx-energy.com",
        "password": "--- password goes here ---",
        "role": "employee",
    },
    {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@maxx-energy.com",
        "password": "--- password goes here ---",
        "role": "guest",
    },
    # Add more users as needed...
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

            # Check if user already exists. If so, skip. This prevents duplicates.
            email = entry["email"].strip().lower()
            if User.query.filter_by(email=email).first():
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
                email=email,
                role=entry["role"]
            )
            user.set_password(password)
            db.session.add(user)
            print(f"User {email} ready to be added to db.")

        try:
            db.session.commit()
            print("All valid users have been created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding users to database: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()