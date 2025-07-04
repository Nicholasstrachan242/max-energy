from db import db, User, Role, Permission
from flask import Flask
import os

# Adjust the import below if your app factory is elsewhere
from app import create_app

app = create_app()

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

def seed_permissions_and_roles():
    with app.app_context():
        # Create permissions
        for name, desc in permissions:
            perm = Permission.query.filter_by(name=name).first()
            if not perm:
                perm = Permission(name=name, description=desc)
                db.session.add(perm)
        db.session.commit()

        # Assign permissions to roles
        for role_name, perm_names in role_permissions.items():
            role = Role.query.filter_by(name=role_name).first()
            if role:
                perms = Permission.query.filter(Permission.name.in_(perm_names)).all()
                role.permissions = perms
        db.session.commit()
        print('Permissions and roles seeded successfully.')

if __name__ == '__main__':
    seed_permissions_and_roles() 