import os, sys, re, getpass
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# run script as module: python -m scripts.<script_name> (without .py extension)

# Add the project root directory to Python path
# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, project_root)

from app import create_app, db
from app.models.User import User

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
        print("=== Maxx Energy Admin: Add User ===")
        # role selection. Limited to admin, executive, manager, employee, guest
        role = input("Role: [ manager | employee | guest ] ").strip().lower()
        if role not in ["manager", "employee", "guest", "admin", "executive"]:
            print("Invalid role. Please choose from: manager, employee, guest.")
            sys.exit(1)
        elif role == "admin" or role == "executive":
            confirm = input("WARNING: This will create an admin/executive user. Are you sure? (y/n): ").strip().lower()
            if confirm != "y":
                print("User creation cancelled.")
                sys.exit(1)
                
        email = input("Email: ").strip().lower()
        if User.query.filter_by(email_hash=User.hash_email(email)).first():
            print("Error: This email is already registered. Cancelling user creation.")
            sys.exit(1)
        
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()

        # loop password creation until valid password is entered
        while True:
            password = getpass.getpass("Password must:\n" + 
                                       "- be at least 12 characters long\n" +
                                       "- contain at least one uppercase letter\n" +
                                       "- contain at least one number\n" +
                                       "- contain at least one symbol.\n" +
                                       "Enter password: ")
            password2 = getpass.getpass("Confirm password: ")
            if password != password2:
                print("Passwords do not match. Please try again.")
                continue
            valid, msg = is_strong_password(password)
            if not valid:
                print(msg)
                continue
            break

        user = User(
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        # uses fernet encrpytion + SHA-256 hashing on email
        # uses scrypt hashing on password
        user.set_email(email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    
        print(f"User {email} created successfully.")
        # log the event
        try:
            log_auth_event("user_created", details="1 user created.")
        except Exception as e:
            print(f"Failed to log auth event: {e}")


if __name__ == "__main__":
    main()