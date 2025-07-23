#!/usr/bin/env python3
"""
Simple Database Setup Script
Creates the database and admin user without using migrations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.rbac.models import RBACUser, RBACRole, RBACPermission
from app.models import User

def simple_setup():
    """Create database and admin user for testing."""
    app = create_app()
    
    with app.app_context():
        print("🔧 Creating database tables...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
        # Create admin role
        admin_role = RBACRole.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = RBACRole(name='admin', description='System Administrator')
            db.session.add(admin_role)
            db.session.commit()
            print("✅ Created admin role")
        
        # Create basic permissions
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
        
        # Create test admin user in RBAC system
        test_admin = RBACUser.query.filter_by(username='testadmin').first()
        if not test_admin:
            test_admin = RBACUser(
                username='testadmin',
                role_id=admin_role.id,
                status='active'
            )
            test_admin.set_password('test123')
            db.session.add(test_admin)
            db.session.commit()
            print("✅ Created RBAC admin user: testadmin")
        
        # Create test admin user in main app system
        main_admin = User.query.filter_by(username='testadmin').first()
        if not main_admin:
            main_admin = User(
                username='testadmin',
                email='testadmin@example.com',
                role='admin'
            )
            main_admin.set_password('test123')
            db.session.add(main_admin)
            db.session.commit()
            print("✅ Created main app admin user: testadmin")
        
        print("\n🎉 Setup Complete!")
        print("=" * 50)
        print("📧 Username: testadmin")
        print("🔑 Password: test123")
        print("👤 Role: admin")
        print("=" * 50)
        print("\n🌐 Test URLs:")
        print("1. Main Login: http://localhost:5000/login")
        print("2. Admin Panel: http://localhost:5000/admin/admins-only")
        print("3. RBAC Dashboard: http://localhost:5000/rbac/dashboard")
        print("\n⚠️  Remember to change the password in production!")

if __name__ == '__main__':
    simple_setup() 