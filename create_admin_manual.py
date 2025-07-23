#!/usr/bin/env python3
"""
Manual Admin User Creation
Run this in Flask shell to create admin user.
"""

import os
# Set email encryption key
os.environ['EMAIL_ENCRYPTION_KEY'] = 'jLzG9a5kKN2fzSr9nUwlOAUukqpWbdzJ-WD6etobT78='

from app import create_app, db
from app.models import User
from app.rbac.models import RBACUser, RBACRole, RBACPermission

def create_admin():
    """Create admin user manually."""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating admin user...")
        
        # Create admin role
        admin_role = RBACRole.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = RBACRole(name='admin', description='System Administrator')
            db.session.add(admin_role)
            db.session.commit()
            print("✅ Created admin role")
        
        # Create permissions
        permissions = [
            ('dashboard_access', 'Access to RBAC dashboard'),
            ('user_read', 'View user information'),
            ('system_admin', 'Full system administration access'),
        ]
        
        for perm_name, perm_desc in permissions:
            permission = RBACPermission.query.filter_by(name=perm_name).first()
            if not permission:
                permission = RBACPermission(name=perm_name, description=perm_desc)
                db.session.add(permission)
                print(f"✅ Created permission: {perm_name}")
        
        db.session.commit()
        
        # Add permissions to admin role
        for perm_name, _ in permissions:
            permission = RBACPermission.query.filter_by(name=perm_name).first()
            if permission and permission not in admin_role.permissions:
                admin_role.permissions.append(permission)
        
        db.session.commit()
        
        # Create main app admin user
        admin_email = 'admin@maxenergy.com'
        admin_user = User.query.filter_by(email_hash=User.hash_email(admin_email)).first()
        if not admin_user:
            admin_user = User(
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            admin_user.set_email(admin_email)
            admin_user.set_password('Admin123!@#')
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Created main app admin user")
        
        # Create RBAC admin user
        rbac_admin = RBACUser.query.filter_by(username='admin').first()
        if not rbac_admin:
            rbac_admin = RBACUser(
                username='admin',
                role_id=admin_role.id,
                status='active'
            )
            rbac_admin.set_password('Admin123!@#')
            db.session.add(rbac_admin)
            db.session.commit()
            print("✅ Created RBAC admin user")
        
        print("\n🎉 Admin User Created Successfully!")
        print("=" * 60)
        print("📧 Email: admin@maxenergy.com")
        print("🔑 Password: Admin123!@#")
        print("👤 Role: admin")
        print("=" * 60)
        print("\n🌐 Login URLs:")
        print("1. Main Login: http://localhost:5000/auth/login")
        print("2. Admin Panel: http://localhost:5000/admin/admins-only")
        print("3. RBAC Dashboard: http://localhost:5000/rbac/dashboard")

if __name__ == '__main__':
    create_admin() 