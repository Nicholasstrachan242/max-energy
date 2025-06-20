# Handle common user-facing HTTP errors here such as:
# 400 Bad Request
# 401 Unauthorized
# 403 Forbidden
# 404 Not Found
# 422 Unprocessable Entity
# 429 Too Many Requests
# 500 Internal Server Error
# 502 Bad Gateway
# 503 Service Unavailable

from flask import redirect, url_for

def register_error_handlers(app):
    @app.errorhandler(429)
    def rate_limit_handler(e):
        return redirect(url_for('home.too_many_requests_page'))
    
    @app.errorhandler(403)
    def forbidden(e):
        return redirect(url_for('home.forbidden_page'))
    
    @app.errorhandler(500)
    def server_error(e):
        return redirect(url_for('home.server_error_page'))
