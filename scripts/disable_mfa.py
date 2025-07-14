import sys, getpass
from app import create_app, db
from app.models import User
from app.auth.auth_logging import log_auth_event

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script deactivates multi-factor authentication for a user account using their login email.
# This should only be used after verifying the identity of the user and their reason for the request.
# For example, if they lose/replace their existing device and need to reconfigure MFA on a new device.

# run script as module: python -m scripts.<script_name> (without .py extension)

def main():
    app = create_app()
    with app.app_context():
        email = input("Enter the user's email to disable Multi-Factor Authentication on their account:").strip()
        user = User.query.filter_by(email_hash=User.hash_email(email)).first()
        if not user:
            print("No user found with that email.")
            sys.exit(1)
        if not user.has_mfa_enabled():
            print("User does not have MFA enabled on their account.")
            sys.exit(0)
        # confirm deactivation
        confirm = input(f"Are you sure you want to disable MFA for {user.get_email()}? (y/n): ")
        if confirm.lower() != 'y':
            print("Action cancelled.")
            sys.exit(0)

        # disable mfa flag AND delete secret
        user.mfa_enabled = False
        user.mfa_secret = None
        db.session.commit()
        
        print(f"MFA for {user.get_email()} has been deactivated.")

        # log the event
        try:
            log_auth_event("mfa_disabled", user_id=user.id)
        except Exception as e:
            print(f"Failed to log auth event: {e}")
        

if __name__ == "__main__":
    main()