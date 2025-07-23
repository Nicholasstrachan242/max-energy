#!/usr/bin/env python3
"""
Quick Test Setup Script
Creates a simple test database and admin user for immediate testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.rbac.models import RBACUser, RBACRole, RBACPermission
from app.models import User

def quick_test_setup():
    """Create a simple test setup with absolute database path."""
    
    # Create app with test configuration
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',  # Use current directory
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    }
    
    # Set email encryption key for testing
    os.environ['EMAIL_ENCRYPTION_KEY'] = 'jLzG9a5kKN2fzSr9nUwlOAUukqpWbdzJ-WD6etobT78='
    
    app = create_app(test_config)
    
    with app.app_context():
        print("🔧 Creating test database...")
        
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
        test_admin = RBACUser.query.filter_by(username='admin').first()
        if not test_admin:
            test_admin = RBACUser(
                username='admin@maxx-energy.com',
                role_id=admin_role.id,
                status='active'
            )
            test_admin.set_password('Password123!')
            db.session.add(test_admin)
            db.session.commit()
            print("✅ Created RBAC admin user: admin")
        
        # Create test admin user in main app system
        main_admin = User.query.filter_by(email_hash=User.hash_email('admin@example.com')).first()
        if not main_admin:
            main_admin = User(
                first_name='Admin',
                last_name='User',
                role='admin'
            )
            main_admin.set_email('admin@example.com')
            main_admin.set_password('admin123')
            db.session.add(main_admin)
            db.session.commit()
            print("✅ Created main app admin user: admin@example.com")
        
        print("\n🎉 Quick Test Setup Complete!")
        print("=" * 50)
        print("📧 Username: admin")
        print("🔑 Password: admin123")
        print("👤 Role: admin")
        print("=" * 50)
        print("\n🌐 Test URLs:")
        print("1. Main Login: http://localhost:5000/login")
        print("2. Admin Panel: http://localhost:5000/admin/admins-only")
        print("3. RBAC Dashboard: http://localhost:5000/rbac/dashboard")
        print("\n⚠️  This is a test setup - change passwords in production!")

if __name__ == '__main__':
    quick_test_setup() 