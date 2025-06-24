import os, sys, re, getpass
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script allows for user password reset.
# Expected use case is when a user forgets their password and cannot access their account.
# A secure password must be created here. Please share the new password with the user in a secure manner.
# The user will then have the ability to log into their account and change their own password through the site UI.

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

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
        email = input("Enter user email: ").strip()
        user = User.query.filter_by(email_hash=User.hash_email(email)).first()
        if not user:
            print("User not found.")
            sys.exit(1)
        # loop password creation until valid password is entered
        while True:
            password = getpass.getpass("Password must:\n" + 
                                       "- be at least 12 characters long\n" +
                                       "- contain at least one uppercase letter\n" +
                                       "- contain at least one number\n" +
                                       "- contain at least one symbol.\n" +
                                       "Enter new password: ")
            password2 = getpass.getpass("Confirm new password: ")
            if password != password2:
                print("Passwords do not match. Please try again.")
                continue
            valid, msg = is_strong_password(password)
            if not valid:
                print(msg)
                continue
            break

        # set password and commit to db
        user.set_password(password)

        # log this event
        log_auth_event("admin_password_change", details=f"Admin script has reset the password for user email hash: {user}")
