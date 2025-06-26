from app import create_app, db
from app.models.User import User
import csv

# WARNING: FOR INTERNAL ADMIN USE ONLY. Do not run or edit this script without prior authorization.

# This script imports a "users.csv" file and creates users in the db.
# users.csv was exported from production db and has 2 columns: 
#   [employee_id] - unique integer, autoincrements
#   [name] - full name
# script does not allow partial data to be committed to db. ALL or NONE only.

# run script as module: python -m scripts.<script_name> (without .py extension)

# split name into first and last
def split_name(full_name):
    parts = full_name.strip().split()
    first_name = parts[0]
    # last name includes middle if present. defaults to NONE since last_name is not nullable
    last_name = ''.join(parts[1:]) if len(parts) > 1 else 'NONE'
    return first_name, last_name

def main(csv_path):
    app = create_app()
    with app.app_context():
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            try:
                for row in reader:
                    employee_id = int(row['employee_id'])
                    first_name, last_name = split_name(row['name'])
                    # email format: firstlast@maxx-energy.com 
                    # last includes middle initial if present.
                    email = f"{first_name.lower()}{last_name.lower()}@maxx-energy.com"
                    # default password used here. 
                    # Employees are instructed to change it as soon as they gain access to their account.
                    password = "--REDACTED--" # TODO: change this before running script

                    user = User(
                        employee_id=employee_id,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    user.set_email(email)
                    user.set_password(password)
                    user.set_role("guest") # default these new users as guests. Principle of Least Privilege.
                    db.session.add(user)
                db.session.commit()
                print("Import complete")
            except Exception as e:
                db.session.rollback()
                print(f"Import failed: {e}")


if __name__ == "__main__":
    main("scripts/users.csv")