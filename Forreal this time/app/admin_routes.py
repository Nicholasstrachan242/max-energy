from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import db, User, Role, Permission, AuditLog
from functools import wraps
from datetime import datetime

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in first.')
            return redirect(url_for('auth.login'))
        user = User.query.filter_by(username=session['username']).first()
        if not user or user.role.name != 'admin':
            flash('Access denied. Admin privileges required.')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/role-management')
@admin_required
def role_management():
    users = User.query.all()
    roles = Role.query.all()
    permissions = Permission.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    return render_template('role_management.html', users=users, roles=roles, permissions=permissions, audit_logs=audit_logs)

@admin_bp.route('/add_user', methods=['POST'])
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
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/edit_user/<int:user_id>', methods=['POST'])
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
        flash('Invalid role selected', 'danger')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot delete admin user', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/add_role', methods=['POST'])
@admin_required
def add_role():
    name = request.form['role_name']
    description = request.form['description']
    if Role.query.filter_by(name=name).first():
        flash('Role already exists', 'danger')
    else:
        db.session.add(Role(name=name, description=description))
        db.session.commit()
        flash('Role added successfully', 'success')
    return redirect(url_for('admin.role_management'))

@admin_bp.route('/edit_role/<int:role_id>', methods=['POST'])
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)
    role.name = request.form['role_name']
    role.description = request.form['description']
    db.session.commit()
    flash('Role updated successfully', 'success')
    return redirect(url_for('admin.role_management'))

@admin_bp.route('/delete_role/<int:role_id>', methods=['POST'])
@admin_required
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)
    if role.name == 'admin':
        flash('Cannot delete admin role', 'danger')
    else:
        db.session.delete(role)
        db.session.commit()
        flash('Role deleted successfully', 'success')
    return redirect(url_for('admin.role_management'))

@admin_bp.route('/add_permission', methods=['POST'])
@admin_required
def add_permission():
    name = request.form['permission_name']
    description = request.form['description']
    if Permission.query.filter_by(name=name).first():
        flash('Permission already exists', 'danger')
    else:
        db.session.add(Permission(name=name, description=description))
        db.session.commit()
        flash('Permission added successfully', 'success')
    return redirect(url_for('admin.role_management'))

@admin_bp.route('/edit_permission/<int:permission_id>', methods=['POST'])
@admin_required
def edit_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    permission.name = request.form['permission_name']
    permission.description = request.form['description']
    db.session.commit()
    flash('Permission updated successfully', 'success')
    return redirect(url_for('admin.role_management'))

@admin_bp.route('/delete_permission/<int:permission_id>', methods=['POST'])
@admin_required
def delete_permission(permission_id):
    permission = Permission.query.get_or_404(permission_id)
    db.session.delete(permission)
    db.session.commit()
    flash('Permission deleted successfully', 'success')
    return redirect(url_for('admin.role_management'))

@admin_bp.route('/admin/assign-permissions', methods=['GET', 'POST'])
@admin_required
def assign_permissions_admin():
    roles = Role.query.all()
    permissions = Permission.query.all()
    if request.method == 'POST':
        role_id = int(request.form['role_id'])
        selected_permissions = request.form.getlist('permissions')
        role = Role.query.get(role_id)
        if role:
            role.permissions = [Permission.query.get(int(pid)) for pid in selected_permissions if Permission.query.get(int(pid))]
            db.session.commit()
            
            # Log the action
            admin_username = session.get('username', 'unknown')
            db.session.add(AuditLog(
                admin_username=admin_username,
                action='assign_permissions',
                target=f'role_{role.name}',
                details=f'Assigned {len(selected_permissions)} permissions to role {role.name} via admin interface'
            ))
            db.session.commit()
            
            flash(f'Permissions updated successfully for role: {role.name}', 'success')
        else:
            flash('Role not found', 'error')
    return render_template('assign_permissions.html', roles=roles, permissions=permissions)

@admin_bp.route('/user-management')
@admin_required
def user_management():
    users = User.query.all()
    roles = Role.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    user_permissions = []
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user_permissions = [perm.name for perm in user.role.permissions]
    return render_template('user_management.html', users=users, roles=roles, audit_logs=audit_logs, user_permissions=user_permissions)

@admin_bp.route('/user-management-auth', methods=['GET', 'POST'])
@admin_required
def user_management_auth():
    if request.method == 'POST':
        print("POST request received")
        print("Form data:", request.form)
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        print(f"Username: {username}, Password length: {len(password)}")
        user = User.query.filter_by(username=username).first()
        if user and user.role.name == 'admin' and user.check_password(password):
            session['user_mgmt_auth'] = True
            db.session.add(AuditLog(admin_username=username, action='admin_auth', target='user_management', details='Admin authenticated for user management access.'))
            db.session.commit()
            return redirect(url_for('admin.user_management'))
        else:
            flash('Invalid admin credentials.')
    return render_template('user_management_auth.html')

@admin_bp.route('/reset_user_password/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_password = request.form['new_password']
        user.set_password(new_password)
        db.session.commit()
        flash('Password reset successfully', 'success')
        return redirect(url_for('admin.user_management'))
    return render_template('reset_user_password.html', user=user)

@admin_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.status == 'active':
        user.status = 'inactive'
    else:
        user.status = 'active'
    db.session.commit()
    flash('User status updated', 'success')
    return redirect(url_for('admin.user_management'))

@admin_bp.route('/assign-role-permissions/<int:role_id>', methods=['GET', 'POST'])
@admin_required
def assign_role_permissions(role_id):
    role = Role.query.get_or_404(role_id)
    permissions = Permission.query.all()
    
    if request.method == 'POST':
        selected_permissions = request.form.getlist('permissions')
        role.permissions = [Permission.query.get(int(pid)) for pid in selected_permissions if Permission.query.get(int(pid))]
        db.session.commit()
        
        # Log the action
        admin_username = session.get('username', 'unknown')
        db.session.add(AuditLog(
            admin_username=admin_username,
            action='assign_permissions',
            target=f'role_{role.name}',
            details=f'Assigned {len(selected_permissions)} permissions to role {role.name}'
        ))
        db.session.commit()
        
        flash(f'Permissions updated successfully for role: {role.name}', 'success')
        return redirect(url_for('admin.role_management'))
    
    return render_template('assign_role_permissions.html', role=role, permissions=permissions)

@admin_bp.route('/assign-user-permissions/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def assign_user_permissions(user_id):
    user = User.query.get_or_404(user_id)
    permissions = Permission.query.all()
    
    if request.method == 'POST':
        selected_permissions = request.form.getlist('permissions')
        user.role.permissions = [Permission.query.get(int(pid)) for pid in selected_permissions if Permission.query.get(int(pid))]
        db.session.commit()
        
        # Log the action
        admin_username = session.get('username', 'unknown')
        db.session.add(AuditLog(
            admin_username=admin_username,
            action='assign_user_permissions',
            target=f'user_{user.username}',
            details=f'Assigned {len(selected_permissions)} permissions to user {user.username}'
        ))
        db.session.commit()
        
        flash(f'Permissions updated successfully for user: {user.username}', 'success')
        return redirect(url_for('admin.user_management'))
    
    return render_template('assign_user_permissions.html', user=user, permissions=permissions)

@admin_bp.route('/permission-management')
@admin_required
def permission_management():
    roles = Role.query.all()
    permissions = Permission.query.all()
    users = User.query.all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('permission_management.html', 
                         roles=roles, 
                         permissions=permissions, 
                         users=users, 
                         audit_logs=audit_logs) 