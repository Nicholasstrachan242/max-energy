from .Algorithm import db

def list_roles():
    roles = db(db.role).select()
    return [role.name for role in roles]

def add_role(name):
    db.role.insert(name=name)

def list_permissions():
    permissions = db(db.permission).select()
    return [permission.name for permission in permissions]

def add_permission(name):
    db.permission.insert(name=name)

def list_role_permissions():
    role_permissions = db(db.role_permission).select()
    return [(rp.role_id, rp.permission_id) for rp in role_permissions]

def add_role_permission(role_id, permission_id):
    db.role_permission.insert(role_id=role_id, permission_id=permission_id)

def list_user_roles():
    user_roles = db(db.user_role).select()
    return [(ur.user_id, ur.role_id) for ur in user_roles]

def add_user_role(user_id, role_id):
    db.user_role.insert(user_id=user_id, role_id=role_id)

if __name__ == "__main__":
    print("--- RBAC Testing Example ---")

    # Add roles
    add_role("Tester")
    print("Roles:", list_roles())

    # Add permissions
    add_permission("view_dashboard")
    add_permission("edit_profile")
    print("Permissions:", list_permissions())

    # Add role_permission (assign permission to role)
    roles = db(db.role).select()
    permissions = db(db.permission).select()
    if roles and permissions:
        add_role_permission(roles.first().id, permissions.first().id)
    print("Role-Permissions:", list_role_permissions())

    # Add user_role (assign role to user_id 1 for example)
    if roles:
        add_user_role(1, roles.first().id)
    print("User-Roles:", list_user_roles()) 