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