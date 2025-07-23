from flask import Blueprint

rbac_bp = Blueprint('rbac', __name__, 
                    url_prefix='/rbac',
                    template_folder='templates',
                    static_folder='static')

from . import routes 