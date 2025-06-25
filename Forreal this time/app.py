from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify # type: ignore
from functools import wraps
from flask_wtf.csrf import CSRFProtect # type: ignore
import secrets
from datetime import datetime
from db import db, User, Role, Permission, AuditLog
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder='statics')
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Create database tables and seed roles
with app.app_context():
    db.create_all()
    # Seed roles
    role_names = [
        ('admin', 'System Administrator'),
        ('executive', 'Executive User'),
        ('manager', 'Manager User'),
        ('staff', 'Staff User'),
        ('guest', 'Guest User')
    ]
    for name, desc in role_names:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=desc))
    db.session.commit()
    # Create default admin role and user if they don't exist
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role and not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', role=admin_role)
        admin_user.set_password('password')
        db.session.add(admin_user)
        db.session.commit()
    # Create default permissions if not exist
    permissions = {
        'manage_users': 'Can manage system users',
        'manage_roles': 'Can manage roles',
        'manage_permissions': 'Can manage permissions',
        'edit_content': 'Can edit content',
        'view_content': 'Can view content',
        'manage_team': 'Can manage their team',
        'view_reports': 'Can view reports'
    }
    for name, description in permissions.items():
        if not Permission.query.filter_by(name=name).first():
            db.session.add(Permission(name=name, description=description))
    db.session.commit()
    # Seed default manager user
    manager_role = Role.query.filter_by(name='manager').first()
    if manager_role and not User.query.filter_by(username='manager').first():
        manager_user = User(username='manager', role=manager_role)
        manager_user.set_password('password')
        db.session.add(manager_user)
        db.session.commit()
    # Seed default executive user
    executive_role = Role.query.filter_by(name='executive').first()
    if executive_role and not User.query.filter_by(username='executive').first():
        executive_user = User(username='executive', role=executive_role)
        executive_user.set_password('password')
        db.session.add(executive_user)
        db.session.commit()
    # Seed default staff user
    staff_role = Role.query.filter_by(name='staff').first()
    if staff_role and not User.query.filter_by(username='staff').first():
        staff_user = User(username='staff', role=staff_role)
        staff_user.set_password('password')
        db.session.add(staff_user)
        db.session.commit()
    # Seed default guest user
    guest_role = Role.query.filter_by(name='guest').first()
    if guest_role and not User.query.filter_by(username='guest').first():
        guest_user = User(username='guest', role=guest_role)
        guest_user.set_password('password')
        db.session.add(guest_user)
        db.session.commit()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=session['username']).first()
        if not user or user.role.name != 'admin':
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            session['role'] = user.role.name
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if user.role.name == 'admin':
                return redirect(url_for('role_management'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/home')
def home():
    # Only allow guests to access home
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user and user.role.name == 'guest':
            session['role'] = user.role.name
            return render_template('home.html')
        else:
            return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=session['username']).first()
    allowed_roles = ['admin', 'executive', 'manager', 'staff']
    if user.role.name in allowed_roles:
        session['role'] = user.role.name
        user_permissions = [perm.name for perm in user.role.permissions]
        return render_template('dashboard.html', user_permissions=user_permissions)
    else:
        flash('Access denied.')
        return redirect(url_for('home'))

@app.route('/role-management')
@admin_required
def role_management():
    users = User.query.all()
    roles = Role.query.all()
    permissions = Permission.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    return render_template('role_management.html', 
                         users=users, 
                         roles=roles, 
                         permissions=permissions,
                         audit_logs=audit_logs)

@app.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    username = request.form['username']
    password = request.form['password']
    role_name = request.form['role']
    
    if User.query.filter_by(username=username).first():
        flash('User already exists', 'danger')
    else:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully', 'success')
        else:
            flash('Invalid role selected', 'danger')
    
    return redirect(url_for('user_management'))

@app.route('/edit_user/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    role_name = request.form['role']
    
    role = Role.query.filter_by(name=role_name).first()
    if role:
        user.role = role
        db.session.commit()
        flash('User updated successfully', 'success')
    else:
        flash('Invalid role', 'danger')
    
    return redirect(url_for('user_management'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot delete admin user')
    else:
        db.session.add(AuditLog(admin_username=session['username'], action='delete_user', target=user.username, details='User deleted.'))
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
    return redirect(url_for('user_management'))

@app.route('/add_role', methods=['POST'])
@admin_required
def add_role():
    name = request.form['role_name'].strip()
    description = request.form['description'].strip()
    if not name or not re.match(r'^[A-Za-z0-9_ ]{3,32}$', name):
        flash('Invalid role name. Use 3-32 alphanumeric characters, spaces, or underscores.')
        return redirect(url_for('role_management'))
    if Role.query.filter_by(name=name).first():
        flash('Role already exists')
    else:
        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        db.session.add(AuditLog(admin_username=session['username'], action='add_role', target=name, details='Role added.'))
        db.session.commit()
        flash('Role added successfully')
    return redirect(url_for('role_management'))

@app.route('/edit_role/<int:role_id>', methods=['POST'])
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    if role.name == 'admin':
        flash('Cannot edit admin role')
        return redirect(url_for('role_management'))
    role.name = request.form['role_name']
    role.description = request.form['description']
    db.session.commit()
    db.session.add(AuditLog(admin_username=session['username'], action='edit_role', target=role.name, details='Role edited.'))
    db.session.commit()
    flash('Role updated successfully')
    return redirect(url_for('role_management'))

@app.route('/delete_role/<int:role_id>', methods=['POST'])
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    if role.name == 'admin':
        flash('Cannot delete admin role')
    else:
        db.session.add(AuditLog(admin_username=session['username'], action='delete_role', target=role.name, details='Role deleted.'))
        db.session.delete(role)
        db.session.commit()
        flash('Role deleted successfully')
    return redirect(url_for('role_management'))

@app.route('/add_permission', methods=['POST'])
@admin_required
def add_permission():
    name = request.form['permission_name']
    description = request.form['description']
    
    if Permission.query.filter_by(name=name).first():
        flash('Permission already exists')
    else:
        permission = Permission(name=name, description=description)
        db.session.add(permission)
        db.session.commit()
        flash('Permission added successfully')
    
    return redirect(url_for('role_management'))

@app.route('/edit_permission/<int:permission_id>', methods=['POST'])
@admin_required
def edit_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    permission.name = request.form['permission_name']
    permission.description = request.form['description']
    db.session.commit()
    flash('Permission updated successfully')
    return redirect(url_for('role_management'))

@app.route('/delete_permission/<int:permission_id>', methods=['POST'])
@admin_required
def delete_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    flash('Permission deleted successfully')
    return redirect(url_for('role_management'))

@app.route('/assign_permission/<int:role_id>', methods=['POST'])
@admin_required
def assign_permission(role_id):
    role = Role.query.get_or_404(role_id)
    permission_id = request.form.get('permission_id')
    permission = Permission.query.get_or_404(permission_id)
    
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.session.commit()
        flash('Permission assigned successfully')
    else:
        flash('Permission already assigned')
    
    return redirect(url_for('role_management'))

@app.route('/remove_permission/<int:role_id>/<int:permission_id>', methods=['POST'])
@admin_required
def remove_permission(role_id, permission_id):
    role = Role.query.get_or_404(role_id)
    permission = Permission.query.get_or_404(permission_id)
    
    if permission in role.permissions:
        role.permissions.remove(permission)
        db.session.commit()
        flash('Permission removed successfully')
    else:
        flash('Permission not assigned to role')
    
    return redirect(url_for('role_management'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/admin/assign-permissions', methods=['GET', 'POST'])
@admin_required
def assign_permissions_admin():
    roles = Role.query.all()
    permissions = Permission.query.all()
    if request.method == 'POST':
        role_id = int(request.form['role_id'])
        selected_permission_ids = request.form.getlist('permissions')
        role = Role.query.get_or_404(role_id)
        # Clear all permissions first
        role.permissions = []
        # Assign selected permissions
        for perm_id in selected_permission_ids:
            perm = Permission.query.get(int(perm_id))
            if perm:
                role.permissions.append(perm)
        db.session.commit()
        flash('Permissions updated for role: ' + role.name)
        return redirect(url_for('assign_permissions_admin'))
    return render_template('assign_permissions.html', roles=roles, permissions=permissions)

@app.route('/access_denied')
def access_denied():
    return render_template('access_denied.html')

@app.route('/user-management-auth', methods=['GET', 'POST'])
@admin_required
def user_management_auth():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.role.name == 'admin' and user.check_password(password):
            session['user_mgmt_auth'] = True
            db.session.add(AuditLog(admin_username=username, action='admin_auth', target='user_management', details='Admin authenticated for user management access.'))
            db.session.commit()
            return redirect(url_for('user_management'))
        else:
            flash('Invalid admin credentials.')
    return render_template('user_management_auth.html')

@app.route('/user-management')
@admin_required
def user_management():
    # Require re-authentication for user management
    if not session.get('user_mgmt_auth'):
        return redirect(url_for('user_management_auth'))
    user = User.query.filter_by(username=session['username']).first()
    user_permissions = [perm.name for perm in user.role.permissions]
    users = User.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    roles = Role.query.order_by(Role.name).all()
    return render_template('user_management.html', users=users, user_permissions=user_permissions, audit_logs=audit_logs, roles=roles)

@app.route('/reset_user_password/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot reset password for admin user.')
        return redirect(url_for('user_management'))
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        if not new_password or len(new_password) < 13:
            flash('Password must be at least 13 characters.')
        else:
            user.set_password(new_password)
            db.session.commit()
            db.session.add(AuditLog(admin_username=session['username'], action='reset_password', target=user.username, details='Password reset by admin.'))
            db.session.commit()
            flash(f"Password for {user.username} has been reset.")
            return redirect(url_for('user_management'))
    return render_template('reset_user_password.html', user=user)

@app.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot deactivate/reactivate admin user.')
    else:
        if user.status == 'active':
            user.status = 'inactive'
            db.session.add(AuditLog(admin_username=session['username'], action='deactivate_user', target=user.username, details='User deactivated.'))
            flash(f"{user.username} has been deactivated.")
        else:
            user.status = 'active'
            db.session.add(AuditLog(admin_username=session['username'], action='reactivate_user', target=user.username, details='User reactivated.'))
            flash(f"{user.username} has been reactivated.")
        db.session.commit()
    return redirect(url_for('user_management'))

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template('429.html'), 429

if __name__ == '__main__':
    app.run(debug=True)
    