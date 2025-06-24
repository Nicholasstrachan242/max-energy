import sys, getpass
from app import create_app, db
from app.models import User
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script reactivates a user account that has been deactivated.

# run script as module: python -m scripts.<script_name> (without .py extension)

def main():
    app = create_app()
    with app.app_context():
        email = input("Enter the user's email to reactivate: ").strip()
        user = User.query.filter_by(email_hash=User.hash_email(email)).first()
        if not user:
            print("No user found with that email.")
            sys.exit(1)
        if user.is_active_flag:
            print("User is already active.")
            sys.exit(0)
        # confirm activation and log event
        confirm = input(f"Are you sure you want to reactivate {user.get_email()}? (y/n): ")
        if confirm.lower() != 'y':
            print("Action cancelled.")
            sys.exit(0)
        user.is_active_flag = True
        db.session.commit()

        print(f"User {user.get_email()} has been reactivated.")
        
        try:
            # log the event
            log_auth_event("user_reactivated", user_id=user.id)
        except Exception as e:
            print(f"Failed to log auth event: {e}")

if __name__ == "__main__":
    main()