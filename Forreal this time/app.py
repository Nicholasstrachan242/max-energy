from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify # type: ignore
from functools import wraps
from flask_wtf.csrf import CSRFProtect # type: ignore
import secrets
from datetime import datetime
from db import db, User, Role, Permission

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)

# Create database tables
with app.app_context():
    db.create_all()
    # Create default admin role and user if they don't exist
    if not Role.query.filter_by(name='admin').first():
        admin_role = Role(name='admin', description='System Administrator')
        db.session.add(admin_role)
        db.session.commit()
        
        # Create default permissions
        permissions = {
            'manage_users': 'Can manage system users',
            'manage_roles': 'Can manage roles',
            'manage_permissions': 'Can manage permissions',
            'edit_content': 'Can edit content',
            'view_content': 'Can view content'
        }
        
        for name, description in permissions.items():
            if not Permission.query.filter_by(name=name).first():
                permission = Permission(name=name, description=description)
                db.session.add(permission)
                admin_role.permissions.append(permission)
        
        db.session.commit()
        
        # Create admin user
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', role=admin_role)
            admin_user.set_password('password')
            db.session.add(admin_user)
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
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if user.role.name == 'admin':
                return redirect(url_for('role_management'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/role-management')
@admin_required
def role_management():
    users = User.query.all()
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('role_management.html', 
                         users=users, 
                         roles=roles, 
                         permissions=permissions)

@app.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    username = request.form['username']
    role_name = request.form['role']
    
    if User.query.filter_by(username=username).first():
        flash('User already exists')
    else:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user = User(username=username, role=role)
            user.set_password('default_password')  # In production, generate a secure password
            db.session.add(user)
            db.session.commit()
            flash('User added successfully')
        else:
            flash('Invalid role')
    
    return redirect(url_for('role_management'))

@app.route('/edit_user/<int:user_id>', methods=['POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    role_name = request.form['role']
    
    role = Role.query.filter_by(name=role_name).first()
    if role:
        user.role = role
        db.session.commit()
        flash('User updated successfully')
    else:
        flash('Invalid role')
    
    return redirect(url_for('role_management'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot delete admin user')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully')
    return redirect(url_for('role_management'))

@app.route('/add_role', methods=['POST'])
@admin_required
def add_role():
    name = request.form['role_name']
    description = request.form['description']
    
    if Role.query.filter_by(name=name).first():
        flash('Role already exists')
    else:
        role = Role(name=name, description=description)
        db.session.add(role)
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
    flash('Role updated successfully')
    return redirect(url_for('role_management'))

@app.route('/delete_role/<int:role_id>', methods=['POST'])
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    if role.name == 'admin':
        flash('Cannot delete admin role')
    else:
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

if __name__ == '__main__':
    app.run(debug=True)
    