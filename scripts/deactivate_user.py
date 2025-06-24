import sys, getpass
from app import create_app, db
from app.models import User
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script deactivates a single user account using their login email.
# Deactivated users are denied access to their dashboard and are given an error message to contact IT support.

# run script as module: python -m scripts.<script_name> (without .py extension)

def main():
    app = create_app()
    with app.app_context():
        email = input("Enter the user's email to deactivate: ").strip()
        user = User.query.filter_by(email_hash=User.hash_email(email)).first()
        if not user:
            print("No user found with that email.")
            sys.exit(1)
        if not user.is_active_flag:
            print("User is already deactivated.")
            sys.exit(0)
        # confirm deactivation
        confirm = input(f"Are you sure you want to deactivate {user.get_email()}? (y/n): ")
        if confirm.lower() != 'y':
            print("Action cancelled.")
            sys.exit(0)
        user.is_active_flag = False
        db.session.commit()
        log_auth_event("user_deactivated", user_id=user.id)
        print(f"User {user.get_email()} has been deactivated.")

if __name__ == "__main__":
    main()