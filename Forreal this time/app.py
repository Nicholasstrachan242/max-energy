from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify # type: ignore
from functools import wraps
from flask_wtf.csrf import CSRFProtect # type: ignore
import secrets
from datetime import datetime
from db import db, User, Role, Permission, AuditLog
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate

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
        if not Permission.query.filter_by(name=name).first():
            db.session.add(Permission(name=name, description=desc))
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
    # Assign permissions to roles
    role_permissions = {
        'staff': [
            'view_site_dashboards', 'view_solar_site_data', 'create_update_maintenance_logs',
            'view_maintenance_history', 'view_company_news', 'request_equipment_orders', 'report_system_issues'
        ],
        'guests': [
            'view_site_dashboards', 'view_company_news'
        ],
        'executives': [
            'view_site_dashboards', 'view_solar_site_data', 'view_maintenance_history', 'view_company_news',
            'access_executive_dashboards', 'view_financial_reports', 'approve_budgets', 'moderate_system_settings'
        ],
        'managers': [
            'view_site_dashboards', 'view_solar_site_data', 'create_update_maintenance_logs',
            'approve_maintenance_requests', 'assign_staff_tasks', 'view_maintenance_history', 'view_company_news',
            'manage_inventory', 'request_equipment_orders', 'report_system_issues', 'moderate_system_settings'
        ]
    }
    for role_name, perms in role_permissions.items():
        role = Role.query.filter_by(name=role_name).first()
        if role:
            role.permissions = [Permission.query.filter_by(name=p).first() for p in perms]
    db.session.commit()

# Register blueprints
from app.auth_routes import auth_bp
from app.admin_routes import admin_bp
from app.main_routes import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
    