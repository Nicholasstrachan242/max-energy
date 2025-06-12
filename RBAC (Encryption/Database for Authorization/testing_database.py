import random
from Encryption.hashing_utils import hash_password, generate_key, encrypt_data
from Encryption.user_model import db, User
import importlib

# Dynamically import the view example module
view_example = importlib.import_module('RBAC (Encryption).view example')
add_role = view_example.add_role
add_permission = view_example.add_permission
add_role_permission = view_example.add_role_permission
add_user_role = view_example.add_user_role
list_roles = view_example.list_roles
list_permissions = view_example.list_permissions
list_role_permissions = view_example.list_role_permissions
list_user_roles = view_example.list_user_roles

# Business office roles and permissions
ROLES = [
    "Admin",
    "Manager",
    "Employee",
    "HR",
    "IT Support"
]
PERMISSIONS = [
    "add_user",
    "edit_user",
    "delete_user",
    "view_reports",
    "edit_reports",
    "access_hr_data",
    "manage_it"
]

USERNAMES = ["alice", "bob", "charlie", "diana", "eve"]
EMAILS = [f"{name}@example.com" for name in USERNAMES]
PASSWORDS = ["password1", "password2", "password3", "password4", "password5"]

# Role-permission mapping for business logic
ROLE_PERMISSIONS = {
    "Admin": PERMISSIONS,  # Admin has all permissions
    "Manager": ["add_user", "edit_user", "view_reports", "edit_reports"],
    "Employee": ["view_reports"],
    "HR": ["add_user", "edit_user", "access_hr_data", "view_reports"],
    "IT Support": ["manage_it", "edit_user", "view_reports"]
}

# User-role mapping for demonstration
USER_ROLES = {
    "alice": ["Admin"],
    "bob": ["Manager"],
    "charlie": ["Employee"],
    "diana": ["HR"],
    "eve": ["IT Support"]
}

def main():
    # Create roles
    for role in ROLES:
        add_role(role)
    print("Roles:", list_roles())

    # Create permissions
    for perm in PERMISSIONS:
        add_permission(perm)
    print("Permissions:", list_permissions())

    # Assign permissions to roles based on business logic
    role_objs = {r.name: r for r in db(db.role).select()}
    perm_objs = {p.name: p for p in db(db.permission).select()}
    for role, perms in ROLE_PERMISSIONS.items():
        role_id = role_objs[role].id
        for perm in perms:
            perm_id = perm_objs[perm].id
            add_role_permission(role_id, perm_id)
    print("Role-Permissions:", list_role_permissions())

    # Create users with hashed passwords and encrypted emails
    key = generate_key()
    user_ids = {}
    for username, email, password in zip(USERNAMES, EMAILS, PASSWORDS):
        password_hash = hash_password(password)
        email_encrypted = encrypt_data(key, email)
        user = User(username=username, password_hash=password_hash, email_encrypted=email_encrypted, encryption_iv=None)
        db.session.add(user)
        db.session.commit()
        user_ids[username] = user.id
        print(f"Created user: {username}, email: {email}")

    # Assign roles to users based on mapping
    for username, roles in USER_ROLES.items():
        user_id = user_ids[username]
        for role in roles:
            role_id = role_objs[role].id
            add_user_role(user_id, role_id)
    print("User-Roles:", list_user_roles())

if __name__ == "__main__":
    main() 