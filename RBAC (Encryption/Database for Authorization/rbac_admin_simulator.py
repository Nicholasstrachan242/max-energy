import importlib
from Encryption.user_model import db, User
from Encryption.hashing_utils import generate_key, encrypt_data, hash_password

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

def print_users():
    users = db.session.query(User).all()
    print("\nUsers:")
    for user in users:
        print(f"  ID: {user.id}, Username: {user.username}")

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
        elif choice == "0":
            print("Exiting RBAC Admin Simulator.")
            break
        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main() 