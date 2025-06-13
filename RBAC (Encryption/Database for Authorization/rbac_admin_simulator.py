import importlib
from Encryption.user_model import db, User
from Encryption.hashing_utils import generate_key, encrypt_data, hash_password
from datetime import datetime, timedelta
import re

# Import RBAC helpers
testing_db = importlib.import_module('RBAC (Encryption).Database for Authorization.testing_database')
view_example = importlib.import_module('RBAC (Encryption).view example')
add_role = view_example.add_role
add_permission = view_example.add_permission
add_role_permission = view_example.add_role_permission
add_user_role = view_example.add_user_role
list_roles = view_example.list_roles
list_permissions = view_example.list_permissions
list_role_permissions = view_example.list_role_permissions
list_user_roles = view_example.list_user_roles

def password_strength_bar(password):
    length = len(password)
    complexity = 0
    if re.search(r'[A-Z]', password):
        complexity += 1
    if re.search(r'[a-z]', password):
        complexity += 1
    if re.search(r'\d', password):
        complexity += 1
    if re.search(r'[^A-Za-z0-9]', password):
        complexity += 1
    score = min(length // 4, 4) + complexity
    bar = '[' + '#' * score + '-' * (8 - score) + ']'
    return bar, score

def is_strong_password(password):
    if len(password) < 15:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[^A-Za-z0-9]', password):
        return False
    return True

def is_unique_password(password):
    # Check against all existing users' password hashes
    users = db.session.query(User).all()
    for user in users:
        if hash_password(password) == user.password_hash:
            return False
    return True

# Example: Assume User model has a password_last_changed field (datetime)
def needs_password_change(user):
    # If password_last_changed is not set, require change
    if not hasattr(user, 'password_last_changed') or user.password_last_changed is None:
        return True
    return (datetime.utcnow() - user.password_last_changed) > timedelta(days=90)

def print_users():
    users = db.session.query(User).all()
    print("\nUsers:")
    for user in users:
        # Check password age if field exists
        change_msg = ""
        if hasattr(user, 'password_last_changed'):
            if needs_password_change(user):
                change_msg = " [Password change required]"
        print(f"  ID: {user.id}, Username: {user.username}{change_msg}")

def print_roles():
    roles = db(db.role).select()
    print("\nRoles:")
    for role in roles:
        print(f"  ID: {role.id}, Name: {role.name}")

def print_permissions():
    permissions = db(db.permission).select()
    print("\nPermissions:")
    for perm in permissions:
        print(f"  ID: {perm.id}, Name: {perm.name}")

def print_user_roles():
    print("\nUser-Role Assignments:")
    for user_id, role_id in list_user_roles()['user_roles']:
        print(f"  User ID: {user_id}, Role ID: {role_id}")

def print_role_permissions():
    print("\nRole-Permission Assignments:")
    for role_id, perm_id in list_role_permissions()['role_permissions']:
        print(f"  Role ID: {role_id}, Permission ID: {perm_id}")

def assign_role_to_user():
    print_users()
    print_roles()
    user_id = int(input("Enter user ID to assign role: "))
    role_id = int(input("Enter role ID to assign: "))
    add_user_role(user_id, role_id)
    print("Role assigned.")

def remove_role_from_user():
    print_user_roles()
    user_id = int(input("Enter user ID to remove role from: "))
    role_id = int(input("Enter role ID to remove: "))
    db(db.user_role.user_id == user_id)(db.user_role.role_id == role_id).delete()
    db.session.commit()
    print("Role removed from user.")

def assign_permission_to_role():
    print_roles()
    print_permissions()
    role_id = int(input("Enter role ID to assign permission: "))
    perm_id = int(input("Enter permission ID to assign: "))
    add_role_permission(role_id, perm_id)
    print("Permission assigned to role.")

def remove_permission_from_role():
    print_role_permissions()
    role_id = int(input("Enter role ID to remove permission from: "))
    perm_id = int(input("Enter permission ID to remove: "))
    db(db.role_permission.role_id == role_id)(db.role_permission.permission_id == perm_id).delete()
    db.session.commit()
    print("Permission removed from role.")

def check_user_permissions():
    print_users()
    user_id = int(input("Enter user ID to check permissions: "))
    # Get all roles for user
    user_roles = [role_id for uid, role_id in list_user_roles()['user_roles'] if uid == user_id]
    # Get all permissions for those roles
    role_perms = [perm_id for role_id, perm_id in list_role_permissions()['role_permissions'] if role_id in user_roles]
    # Get permission names
    perm_objs = {p.id: p.name for p in db(db.permission).select()}
    perms = set(perm_objs[pid] for pid in role_perms)
    print(f"User ID {user_id} has permissions: {', '.join(perms) if perms else 'None'}")

# Example function for creating a user with password policy enforcement
def create_user():
    username = input("Enter new username: ")
    while True:
        password = input("Enter password (at least 15 chars, upper, lower, digit, special, unique): ")
        bar, score = password_strength_bar(password)
        print(f"Password strength: {bar}")
        if not is_strong_password(password):
            print("Password is not strong enough. Please use at least 15 characters, with upper, lower, digit, and special character.")
            continue
        if not is_unique_password(password):
            print("Password is not unique. Please choose a different password.")
            continue
        break
    email = input("Enter email: ")
    key = generate_key()
    password_hash = hash_password(password)
    email_encrypted = encrypt_data(key, email)
    user = User(username=username, password_hash=password_hash, email_encrypted=email_encrypted, encryption_iv=None, password_last_changed=datetime.utcnow())
    db.session.add(user)
    db.session.commit()
    print(f"User {username} created. Encourage using a unique password!")

def main():
    print("\n--- RBAC Admin Simulator ---")
    while True:
        print("\nOptions:")
        print("1. View all users")
        print("2. View all roles")
        print("3. View all permissions")
        print("4. View user-role assignments")
        print("5. View role-permission assignments")
        print("6. Assign role to user")
        print("7. Remove role from user")
        print("8. Assign permission to role")
        print("9. Remove permission from role")
        print("10. Check user permissions")
        print("11. Create new user (with strong password policy)")
        print("0. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            print_users()
        elif choice == "2":
            print_roles()
        elif choice == "3":
            print_permissions()
        elif choice == "4":
            print_user_roles()
        elif choice == "5":
            print_role_permissions()
        elif choice == "6":
            assign_role_to_user()
        elif choice == "7":
            remove_role_from_user()
        elif choice == "8":
            assign_permission_to_role()
        elif choice == "9":
            remove_permission_from_role()
        elif choice == "10":
            check_user_permissions()
        elif choice == "11":
            create_user()
        elif choice == "0":
            print("Exiting RBAC Admin Simulator.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main() 