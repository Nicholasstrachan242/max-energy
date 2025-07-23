# RBAC Integration Guide: Access Point Routes

## 📋 **Overview**
This guide shows how to integrate the RBAC system from `/Forreal this time` into the main `/app` as access point routes, allowing users and admins to access RBAC functionality from the main application.

---

## 🎯 **Integration Strategy**

### **Approach: Blueprint Integration with URL Prefixes**
- **Main App:** `/app` (existing Flask application)
- **RBAC Access:** `/rbac/*` routes within main app
- **Database:** Use main app's MySQL database
- **Authentication:** Unified login system

---

## 📁 **Step 1: Create RBAC Directory Structure**

### **Create the RBAC module in main app:**
```bash
# In /app directory
mkdir -p app/rbac
mkdir -p app/rbac/templates
mkdir -p app/rbac/static
```

### **Directory Structure:**
```
app/
├── __init__.py
├── auth/
├── general/
├── models/
├── rbac/                    # NEW: RBAC module
│   ├── __init__.py
│   ├── models.py           # RBAC database models
│   ├── auth_routes.py      # RBAC authentication
│   ├── admin_routes.py     # RBAC admin functions
│   ├── main_routes.py      # RBAC main routes
│   ├── templates/          # RBAC templates
│   └── static/             # RBAC static files
└── error_handlers.py
```

---

## 🔧 **Step 2: Migrate RBAC Models**

### **Create `app/rbac/models.py`:**
```python
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class RBACUser(db.Model):
    __tablename__ = 'rbac_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('rbac_roles.id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    role = db.relationship('RBACRole', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class RBACRole(db.Model):
    __tablename__ = 'rbac_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    permissions = db.relationship('RBACPermission', 
                                secondary='rbac_role_permission',
                                backref=db.backref('roles', lazy='dynamic'))

class RBACPermission(db.Model):
    __tablename__ = 'rbac_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Association table for Role-Permission many-to-many relationship
rbac_role_permission = db.Table('rbac_role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('rbac_roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('rbac_permissions.id'), primary_key=True)
)

class RBACAuditLog(db.Model):
    __tablename__ = 'rbac_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🛣️ **Step 3: Create RBAC Blueprints**

### **Create `app/rbac/__init__.py`:**
```python
from flask import Blueprint

# Create RBAC blueprints
rbac_auth_bp = Blueprint('rbac_auth', __name__, url_prefix='/rbac/auth')
rbac_admin_bp = Blueprint('rbac_admin', __name__, url_prefix='/rbac/admin')
rbac_main_bp = Blueprint('rbac_main', __name__, url_prefix='/rbac')

# Import routes
from . import auth_routes, admin_routes, main_routes
```

### **Create `app/rbac/auth_routes.py`:**
```python
from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from . import rbac_auth_bp
from .models import RBACUser, RBACRole, RBACAuditLog
from app import db
from datetime import datetime

def rbac_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'rbac_username' not in session:
            flash('Please log in to RBAC system first.')
            return redirect(url_for('rbac_auth.login'))
        user = RBACUser.query.filter_by(username=session['rbac_username']).first()
        if not user or user.role.name != 'admin':
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('rbac_main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@rbac_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = RBACUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['rbac_username'] = username
            session['rbac_role'] = user.role.name
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log the login
            db.session.add(RBACAuditLog(
                admin_username=username,
                action='login',
                target='rbac_system',
                details='User logged into RBAC system'
            ))
            db.session.commit()
            
            flash('Successfully logged into RBAC system!')
            return redirect(url_for('rbac_main.dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template('rbac/login.html')

@rbac_auth_bp.route('/logout')
def logout():
    if 'rbac_username' in session:
        username = session['rbac_username']
        session.pop('rbac_username', None)
        session.pop('rbac_role', None)
        
        # Log the logout
        db.session.add(RBACAuditLog(
            admin_username=username,
            action='logout',
            target='rbac_system',
            details='User logged out of RBAC system'
        ))
        db.session.commit()
        
        flash('Successfully logged out of RBAC system!')
    
    return redirect(url_for('rbac_main.dashboard'))
```

### **Create `app/rbac/admin_routes.py`:**
```python
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from . import rbac_admin_bp
from .models import RBACUser, RBACRole, RBACPermission, RBACAuditLog
from app import db
from datetime import datetime

@rbac_admin_bp.route('/user-management')
@rbac_admin_required
def user_management():
    users = RBACUser.query.all()
    roles = RBACRole.query.all()
    audit_logs = RBACAuditLog.query.order_by(RBACAuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('rbac/user_management.html', 
                         users=users, 
                         roles=roles, 
                         audit_logs=audit_logs)

@rbac_admin_bp.route('/role-management')
@rbac_admin_required
def role_management():
    users = RBACUser.query.all()
    roles = RBACRole.query.all()
    permissions = RBACPermission.query.all()
    audit_logs = RBACAuditLog.query.order_by(RBACAuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('rbac/role_management.html', 
                         users=users, 
                         roles=roles, 
                         permissions=permissions, 
                         audit_logs=audit_logs)

@rbac_admin_bp.route('/assign-permissions/<int:role_id>', methods=['GET', 'POST'])
@rbac_admin_required
def assign_role_permissions(role_id):
    role = RBACRole.query.get_or_404(role_id)
    permissions = RBACPermission.query.all()
    
    if request.method == 'POST':
        selected_permissions = request.form.getlist('permissions')
        role.permissions = [RBACPermission.query.get(int(pid)) for pid in selected_permissions if RBACPermission.query.get(int(pid))]
        db.session.commit()
        
        # Log the action
        admin_username = session.get('rbac_username', 'unknown')
        db.session.add(RBACAuditLog(
            admin_username=admin_username,
            action='assign_permissions',
            target=f'role_{role.name}',
            details=f'Assigned {len(selected_permissions)} permissions to role {role.name}'
        ))
        db.session.commit()
        
        flash(f'Permissions updated successfully for role: {role.name}', 'success')
        return redirect(url_for('rbac_admin.role_management'))
    
    return render_template('rbac/assign_role_permissions.html', role=role, permissions=permissions)

# Add more admin routes as needed...
```

### **Create `app/rbac/main_routes.py`:**
```python
from flask import render_template, session, redirect, url_for
from . import rbac_main_bp
from .models import RBACUser, RBACRole, RBACPermission

@rbac_main_bp.route('/')
def dashboard():
    if 'rbac_username' not in session:
        return redirect(url_for('rbac_auth.login'))
    
    user = RBACUser.query.filter_by(username=session['rbac_username']).first()
    if not user:
        session.pop('rbac_username', None)
        session.pop('rbac_role', None)
        return redirect(url_for('rbac_auth.login'))
    
    return render_template('rbac/dashboard.html', user=user)

@rbac_main_bp.route('/permissions')
def view_permissions():
    if 'rbac_username' not in session:
        return redirect(url_for('rbac_auth.login'))
    
    user = RBACUser.query.filter_by(username=session['rbac_username']).first()
    if not user:
        return redirect(url_for('rbac_auth.login'))
    
    return render_template('rbac/permissions.html', user=user)
```

---

## 🔧 **Step 4: Update Main App Configuration**

### **Update `app/__init__.py`:**
```python
def create_app(test_config=None):
    # ... existing configuration ...
    
    # Register existing blueprints
    from app.general.home import home_bp as home
    from app.auth.auth import auth_bp as auth
    from app.general.dashboard import dashboard_bp as dashboard
    from app.general.contact import contact_bp as contact
    from app.general.admin import admin_bp as admin
    
    # Register RBAC blueprints
    from app.rbac import rbac_auth_bp, rbac_admin_bp, rbac_main_bp
    
    app.register_blueprint(home)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(contact)
    app.register_blueprint(admin)
    
    # RBAC with URL prefixes
    app.register_blueprint(rbac_auth_bp)
    app.register_blueprint(rbac_admin_bp)
    app.register_blueprint(rbac_main_bp)
    
    return app
```

---

## 🎨 **Step 5: Create RBAC Templates**

### **Create `app/rbac/templates/rbac/base.html`:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}RBAC System{% endblock %} - Maxx Energy</title>
    <style>
        body {
            background: linear-gradient(135deg, #496DA7 0%, #FBB019 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 2rem;
        }
        .container {
            background: #fff;
            max-width: 1200px;
            margin: 0 auto;
            border-radius: 12px;
            box-shadow: 0 0 24px #496DA744;
            padding: 2.5rem 2rem;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }
        .btn {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            text-align: center;
            transition: all 0.2s;
            margin: 0 0.5rem;
        }
        .btn-primary {
            background: #496DA7;
            color: #fff;
        }
        .btn-secondary {
            background: #6c757d;
            color: #fff;
        }
        .btn-success {
            background: #FBB019;
            color: #fff;
        }
    </style>
    {% block extra_css %}{% endblock %}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{% block header %}RBAC System{% endblock %}</h1>
            <div>
                {% if session.get('rbac_username') %}
                    <span>Welcome, {{ session.get('rbac_username') }} ({{ session.get('rbac_role') }})</span>
                    <a href="{{ url_for('rbac_auth.logout') }}" class="btn btn-secondary">Logout</a>
                {% else %}
                    <a href="{{ url_for('rbac_auth.login') }}" class="btn btn-primary">Login</a>
                {% endif %}
                <a href="{{ url_for('home.index') }}" class="btn btn-secondary">Main App</a>
            </div>
        </div>
        
        {% with messages = get_flashed_messages() %}
        {% if messages %}
        <div class="flash-messages">
            {% for message in messages %}
            <div class="flash-message">{{ message }}</div>
            {% endfor %}
        </div>
        {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### **Create `app/rbac/templates/rbac/login.html`:**
```html
{% extends "rbac/base.html" %}

{% block title %}RBAC Login{% endblock %}
{% block header %}RBAC System Login{% endblock %}

{% block content %}
<div style="max-width: 400px; margin: 0 auto; text-align: center;">
    <h2>Access RBAC System</h2>
    <form method="POST">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
        <div style="margin-bottom: 1rem;">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required style="width: 100%; padding: 0.5rem;">
        </div>
        <div style="margin-bottom: 1rem;">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required style="width: 100%; padding: 0.5rem;">
        </div>
        <button type="submit" class="btn btn-success">Login to RBAC</button>
    </form>
</div>
{% endblock %}
```

### **Create `app/rbac/templates/rbac/dashboard.html`:**
```html
{% extends "rbac/base.html" %}

{% block title %}RBAC Dashboard{% endblock %}
{% block header %}RBAC Dashboard{% endblock %}

{% block content %}
<div>
    <h2>Welcome to RBAC System</h2>
    <p>You are logged in as: <strong>{{ user.username }}</strong> ({{ user.role.name }})</p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-top: 2rem;">
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
            <h3>User Management</h3>
            <p>Manage users, roles, and permissions</p>
            <a href="{{ url_for('rbac_admin.user_management') }}" class="btn btn-primary">Access</a>
        </div>
        
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
            <h3>Role Management</h3>
            <p>Create and manage roles</p>
            <a href="{{ url_for('rbac_admin.role_management') }}" class="btn btn-primary">Access</a>
        </div>
        
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
            <h3>Your Permissions</h3>
            <p>View your current permissions</p>
            <a href="{{ url_for('rbac_main.view_permissions') }}" class="btn btn-primary">View</a>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🔄 **Step 6: Database Migration**

### **Create migration script:**
```python
# scripts/migrate_rbac.py
from app import create_app, db
from app.rbac.models import RBACUser, RBACRole, RBACPermission, RBACAuditLog, rbac_role_permission

def migrate_rbac_data():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Seed roles
        roles = [
            ('admin', 'System Administrator'),
            ('executive', 'Executive User'),
            ('manager', 'Manager User'),
            ('staff', 'Staff User'),
            ('guest', 'Guest User')
        ]
        
        for name, desc in roles:
            if not RBACRole.query.filter_by(name=name).first():
                role = RBACRole(name=name, description=desc)
                db.session.add(role)
        
        db.session.commit()
        
        # Seed permissions
        permissions = [
            ('view_site_dashboards', 'View site dashboards'),
            ('view_solar_site_data', 'View solar site data'),
            ('create_update_maintenance_logs', 'Create/update maintenance logs'),
            ('approve_maintenance_requests', 'Approve maintenance requests'),
            ('assign_staff_tasks', 'Assign staff tasks'),
            ('view_maintenance_history', 'View maintenance history'),
            ('view_company_news', 'View company news/announcements'),
            ('access_executive_dashboards', 'Access executive dashboards'),
            ('view_financial_reports', 'View financial/compliance reports'),
            ('approve_budgets', 'Approve budgets/major purchases'),
            ('manage_inventory', 'View and manage inventory'),
            ('request_equipment_orders', 'Request equipment orders'),
            ('report_system_issues', 'Report system issues'),
            ('moderate_system_settings', 'Moderate system settings'),
        ]
        
        for name, desc in permissions:
            if not RBACPermission.query.filter_by(name=name).first():
                perm = RBACPermission(name=name, description=desc)
                db.session.add(perm)
        
        db.session.commit()
        
        # Create default admin user
        admin_role = RBACRole.query.filter_by(name='admin').first()
        if admin_role and not RBACUser.query.filter_by(username='admin').first():
            admin_user = RBACUser(username='admin', role=admin_role)
            admin_user.set_password('password')
            db.session.add(admin_user)
            db.session.commit()
        
        print("RBAC migration completed successfully!")

if __name__ == '__main__':
    migrate_rbac_data()
```

---

## 🔗 **Step 7: Add Navigation Links**

### **Update main app templates to include RBAC access:**
```html
<!-- In main app templates, add RBAC access link -->
{% if session.get('username') %}
    <a href="{{ url_for('rbac_main.dashboard') }}" class="btn btn-primary">Access RBAC System</a>
{% endif %}
```

---

## 🎯 **Step 8: Final URL Structure**

### **Access Points:**
```
Main App:
- / (home)
- /auth/login
- /dashboard
- /contact
- /admin

RBAC System (Access Points):
- /rbac/ (RBAC dashboard)
- /rbac/auth/login (RBAC login)
- /rbac/auth/logout (RBAC logout)
- /rbac/admin/user-management
- /rbac/admin/role-management
- /rbac/admin/assign-permissions/<role_id>
- /rbac/permissions (view user permissions)
```

---

## ✅ **Step 9: Testing Checklist**

- [ ] **Database Migration:** Run migration script successfully
- [ ] **RBAC Login:** Test login with admin credentials
- [ ] **User Management:** Create, edit, delete users
- [ ] **Role Management:** Create, edit, delete roles
- [ ] **Permission Assignment:** Assign permissions to roles
- [ ] **Audit Logging:** Verify audit logs are created
- [ ] **Navigation:** Test links between main app and RBAC
- [ ] **Security:** Test access control and permissions
- [ ] **Session Management:** Test login/logout functionality

---

## 🚀 **Step 10: Deployment**

### **Update requirements.txt:**
```
# Add any additional RBAC dependencies
flask-wtf
flask-limiter
```

### **Environment Variables:**
```bash
# Add to .env file
RBAC_ENABLED=true
RBAC_ADMIN_EMAIL=admin@maxxenergy.com
```

---

## 📝 **Usage Instructions**

### **For Users:**
1. Log into main app
2. Click "Access RBAC System" link
3. Log into RBAC system with separate credentials
4. View/manage permissions as needed

### **For Admins:**
1. Access RBAC system with admin credentials
2. Manage users, roles, and permissions
3. View audit logs for security monitoring
4. Assign permissions to roles and users

---

## 🔐 **Security Notes**

- **Separate Sessions:** RBAC uses separate session variables (`rbac_username`, `rbac_role`)
- **Access Control:** Admin functions require `rbac_admin_required` decorator
- **Audit Logging:** All actions are logged for security compliance
- **CSRF Protection:** All forms include CSRF tokens
- **Password Security:** Uses Werkzeug's secure password hashing

This integration provides a clean, secure way to access RBAC functionality from your main application while maintaining separation of concerns and security. 