from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from . import rbac_bp
from .models import RBACUser, RBACRole, RBACPermission, RBACAuditLog, rbac_role_permission
from app import db
from datetime import datetime

# Helper function to log audit events
def log_audit_event(action, target, details=""):
    if 'admin_username' in session:
        log = RBACAuditLog(
            admin_username=session['admin_username'],
            action=action,
            target=target,
            details=details
        )
        db.session.add(log)
        db.session.commit()

# RBAC Dashboard
@rbac_bp.route('/dashboard')
@login_required
def dashboard():
    users = RBACUser.query.all()
    roles = RBACRole.query.all()
    permissions = RBACPermission.query.all()
    
    return render_template('rbac/dashboard.html', 
                         users=users, 
                         roles=roles, 
                         permissions=permissions)

# User Management
@rbac_bp.route('/users')
@login_required
def user_management():
    users = RBACUser.query.all()
    roles = RBACRole.query.all()
    return render_template('rbac/user_management.html', users=users, roles=roles)

@rbac_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role_id = request.form.get('role_id')
        
        if RBACUser.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('rbac.user_management'))
        
        user = RBACUser(username=username, role_id=role_id)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_audit_event('create_user', username)
        flash('User created successfully', 'success')
        return redirect(url_for('rbac.user_management'))
    
    roles = RBACRole.query.all()
    return render_template('rbac/create_user.html', roles=roles)

@rbac_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = RBACUser.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.role_id = request.form.get('role_id')
        user.status = request.form.get('status')
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        log_audit_event('edit_user', user.username)
        flash('User updated successfully', 'success')
        return redirect(url_for('rbac.user_management'))
    
    roles = RBACRole.query.all()
    return render_template('rbac/edit_user.html', user=user, roles=roles)

@rbac_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    user = RBACUser.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    log_audit_event('delete_user', username)
    flash('User deleted successfully', 'success')
    return redirect(url_for('rbac.user_management'))

# Role Management
@rbac_bp.route('/roles')
@login_required
def role_management():
    roles = RBACRole.query.all()
    permissions = RBACPermission.query.all()
    return render_template('rbac/role_management.html', roles=roles, permissions=permissions)

@rbac_bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
def create_role():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        permission_ids = request.form.getlist('permissions')
        
        if RBACRole.query.filter_by(name=name).first():
            flash('Role name already exists', 'error')
            return redirect(url_for('rbac.role_management'))
        
        role = RBACRole(name=name, description=description)
        db.session.add(role)
        db.session.flush()  # Get the ID
        
        # Add permissions
        for perm_id in permission_ids:
            permission = RBACPermission.query.get(perm_id)
            if permission:
                role.permissions.append(permission)
        
        db.session.commit()
        log_audit_event('create_role', name)
        flash('Role created successfully', 'success')
        return redirect(url_for('rbac.role_management'))
    
    permissions = RBACPermission.query.all()
    return render_template('rbac/create_role.html', permissions=permissions)

@rbac_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_role(role_id):
    role = RBACRole.query.get_or_404(role_id)
    
    if request.method == 'POST':
        role.name = request.form.get('name')
        role.description = request.form.get('description')
        
        # Update permissions
        role.permissions.clear()
        permission_ids = request.form.getlist('permissions')
        for perm_id in permission_ids:
            permission = RBACPermission.query.get(perm_id)
            if permission:
                role.permissions.append(permission)
        
        db.session.commit()
        log_audit_event('edit_role', role.name)
        flash('Role updated successfully', 'success')
        return redirect(url_for('rbac.role_management'))
    
    permissions = RBACPermission.query.all()
    return render_template('rbac/edit_role.html', role=role, permissions=permissions)

@rbac_bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
def delete_role(role_id):
    role = RBACRole.query.get_or_404(role_id)
    name = role.name
    db.session.delete(role)
    db.session.commit()
    
    log_audit_event('delete_role', name)
    flash('Role deleted successfully', 'success')
    return redirect(url_for('rbac.role_management'))

# Permission Management
@rbac_bp.route('/permissions')
@login_required
def permission_management():
    permissions = RBACPermission.query.all()
    return render_template('rbac/permission_management.html', permissions=permissions)

@rbac_bp.route('/permissions/create', methods=['GET', 'POST'])
@login_required
def create_permission():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if RBACPermission.query.filter_by(name=name).first():
            flash('Permission name already exists', 'error')
            return redirect(url_for('rbac.permission_management'))
        
        permission = RBACPermission(name=name, description=description)
        db.session.add(permission)
        db.session.commit()
        
        log_audit_event('create_permission', name)
        flash('Permission created successfully', 'success')
        return redirect(url_for('rbac.permission_management'))
    
    return render_template('rbac/create_permission.html')

# Audit Logs
@rbac_bp.route('/audit-logs')
@login_required
def audit_logs():
    logs = RBACAuditLog.query.order_by(RBACAuditLog.timestamp.desc()).limit(100).all()
    return render_template('rbac/audit_logs.html', logs=logs)

# API Endpoints for AJAX
@rbac_bp.route('/api/users/<int:user_id>/permissions')
@login_required
def get_user_permissions(user_id):
    user = RBACUser.query.get_or_404(user_id)
    permissions = [perm.name for perm in user.role.permissions]
    return jsonify({'permissions': permissions})

@rbac_bp.route('/api/roles/<int:role_id>/permissions')
@login_required
def get_role_permissions(role_id):
    role = RBACRole.query.get_or_404(role_id)
    permissions = [{'id': perm.id, 'name': perm.name} for perm in role.permissions]
    return jsonify({'permissions': permissions}) 