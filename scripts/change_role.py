import sys, getpass
from app import create_app, db
from app.models import User
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script changes the role for a single user account using their email.

# run script as module: python -m scripts.<script_name> (without .py extension)

def main():
    app = create_app()
    with app.app_context():
        email = input("Enter the user's email to change their role: ").strip().lower()
        user = User.query.filter_by(email_hash=User.hash_email(email)).first()
        if not user:
            print("No user found with that email.")
            sys.exit(1)
        # prompt for choice of role. Admin and executive are valid but are not displayed as options.
        role = input("Enter new role for user [ guest | employee | manager ]: ").strip().lower()
        if role not in ["guest", "employee", "manager", "executive", "admin"]:
            print("Invalid role. Please choose an option from: [ guest | employee | manager ]")
            sys.exit(1)
        elif role == "admin" or role == "executive":
            confirm = input("WARNING: This will grant the user admin or executive privileges. Are you sure? (y/n): ").strip().lower()
            if confirm != "y":
                print("Role change cancelled.")
                sys.exit(1)
        # do nothing if role is same
        elif role == user.role:
            print("User already has this role. Cancelling.")
            sys.exit(1)

        user.set_role(role)
        db.session.commit()
        
        print(f"User {user.get_email()} has been granted role {user.role}.")

        # log the event
        try:
            log_auth_event("user_role_change", user_id=user.id, details=f"User role changed to {user.role}")
        except Exception as e:
            print(f"Failed to log auth event: {e}")

if __name__ == "__main__":
    main()