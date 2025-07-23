#!/usr/bin/env python3
"""
RBAC Database Seeding Script
Creates initial roles, permissions, and admin user for the RBAC system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.rbac.models import RBACUser, RBACRole, RBACPermission
from werkzeug.security import generate_password_hash

def seed_rbac():
    """Seed the RBAC database with initial data."""
    app = create_app()
    
    with app.app_context():
        # Create permissions
        permissions = [
            # User management permissions
            ('user_create', 'Create new users'),
            ('user_read', 'View user information'),
            ('user_update', 'Edit user information'),
            ('user_delete', 'Delete users'),
            
            # Role management permissions
            ('role_create', 'Create new roles'),
            ('role_read', 'View role information'),
            ('role_update', 'Edit role information'),
            ('role_delete', 'Delete roles'),
            
            # Permission management permissions
            ('permission_create', 'Create new permissions'),
            ('permission_read', 'View permission information'),
            ('permission_update', 'Edit permission information'),
            ('permission_delete', 'Delete permissions'),
            
            # System permissions
            ('system_admin', 'Full system administration access'),
            ('audit_logs', 'View audit logs'),
            ('dashboard_access', 'Access to RBAC dashboard'),
        ]
        
        print("Creating permissions...")
        for perm_name, perm_desc in permissions:
            if not RBACPermission.query.filter_by(name=perm_name).first():
                permission = RBACPermission(name=perm_name, description=perm_desc)
                db.session.add(permission)
                print(f"  - Created permission: {perm_name}")
        
        db.session.commit()
        print("Permissions created successfully!")
        
        # Create roles
        roles = [
            ('admin', 'System Administrator', [
                'user_create', 'user_read', 'user_update', 'user_delete',
                'role_create', 'role_read', 'role_update', 'role_delete',
                'permission_create', 'permission_read', 'permission_update', 'permission_delete',
                'system_admin', 'audit_logs', 'dashboard_access'
            ]),
            ('user_manager', 'User Manager', [
                'user_create', 'user_read', 'user_update', 'user_delete',
                'dashboard_access'
            ]),
            ('role_manager', 'Role Manager', [
                'role_create', 'role_read', 'role_update', 'role_delete',
                'permission_read', 'dashboard_access'
            ]),
            ('viewer', 'Viewer', [
                'user_read', 'role_read', 'permission_read', 'dashboard_access'
            ]),
        ]
        
        print("\nCreating roles...")
        for role_name, role_desc, role_perms in roles:
            if not RBACRole.query.filter_by(name=role_name).first():
                role = RBACRole(name=role_name, description=role_desc)
                db.session.add(role)
                db.session.flush()  # Get the ID
                
                # Add permissions to role
                for perm_name in role_perms:
                    permission = RBACPermission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)
                
                print(f"  - Created role: {role_name} with {len(role_perms)} permissions")
        
        db.session.commit()
        print("Roles created successfully!")
        
        # Create admin user
        admin_role = RBACRole.query.filter_by(name='admin').first()
        if admin_role and not RBACUser.query.filter_by(username='admin').first():
            admin_user = RBACUser(
                username='admin',
                role_id=admin_role.id,
                status='active'
            )
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            db.session.commit()
            print("\nCreated admin user:")
            print("  Username: admin")
            print("  Password: admin123")
            print("  Role: admin")
            print("\n⚠️  IMPORTANT: Change the admin password immediately!")
        
        print("\nRBAC seeding completed successfully!")
        print("\nSummary:")
        print(f"  - {RBACPermission.query.count()} permissions")
        print(f"  - {RBACRole.query.count()} roles")
        print(f"  - {RBACUser.query.count()} users")

if __name__ == '__main__':
    seed_rbac() 