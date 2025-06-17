# RBAC System Development Notes

## Project Overview
A Role-Based Access Control (RBAC) system built with Flask, featuring user authentication, role management, and permission management capabilities.

## How to Run the Application

### Step 1: Set Up the Environment
1. Open your terminal/command prompt
2. Navigate to the project directory:
   ```bash
   cd "Forreal this time"
   ```

### Step 2: Install Dependencies
1. Install required packages:
   ```bash
   pip install flask flask-sqlalchemy flask-wtf werkzeug
   ```

### Step 3: Run the Flask Application
1. Start the Flask server:
   ```bash
   python app.py
   ```
2. You should see output similar to:
   ```
   * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
   * Restarting with stat
   * Debugger is active!
   * Debugger PIN: xxx-xxx-xxx
   ```

### Step 4: Access the Application
1. Open your web browser
2. Go to: `http://127.0.0.1:5000` or `http://localhost:5000`
3. You should see the login page

### Step 5: Log In
1. Use the default admin credentials:
   - Username: `admin`
   - Password: `password`

### Step 6: Stop the Server
1. To stop the Flask server, press `CTRL+C` in the terminal

### Troubleshooting
- If port 5000 is in use, you can change it in `app.py`:
  ```python
  if __name__ == '__main__':
      app.run(debug=True, port=5001)  # Change port number as needed
  ```
- If you get a "Module not found" error, make sure all dependencies are installed
- If the database isn't created, the application will create it automatically on first run

## Components Added

### 1. Database Models (`db.py`)
- **User Model**
  - Username, password hash, role association
  - Last login tracking
  - Password hashing methods
- **Role Model**
  - Name and description
  - Many-to-many relationship with permissions
- **Permission Model**
  - Name and description
  - Association with roles

### 2. Main Application (`app.py`)
- Flask application setup with security features
- Database integration using SQLAlchemy
- CSRF protection implementation
- Route handlers for:
  - User authentication (login/logout)
  - Role management
  - Permission management
  - User management

### 3. Templates
- **Login Page (`login.html`)**
  - Modern UI with gradient background
  - Form validation
  - CSRF protection
  - Error message handling
- **Dashboard (`dashboard.html`)**
  - User welcome page
  - Navigation to role management
- **Role Management (`role_management.html`)**
  - User management interface
  - Role management interface
  - Permission management interface
  - Modal dialogs for edit/delete operations

## Security Features Implemented
1. Password hashing using Werkzeug
2. CSRF protection using Flask-WTF
3. Session management
4. Admin-only access control
5. Protected routes using decorators

## Default Setup
- Admin user created automatically
  - Username: `admin`
  - Password: `password`
- Default admin role with full permissions
- Default permissions:
  - manage_users
  - manage_roles
  - manage_permissions
  - edit_content
  - view_content

## Dependencies
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Werkzeug
- SQLite (database)

## Recent Changes
1. Removed Flask-Limiter due to configuration issues
2. Enhanced login route with better error handling
3. Added CSRF token to login form
4. Improved form validation and security

## Next Steps
1. Implement password reset functionality
2. Add user profile management
3. Implement audit logging
4. Add more granular permission controls
5. Enhance UI/UX features

## Testing Instructions
1. Run the Flask application
2. Access the login page
3. Log in with admin credentials
4. Test role and permission management features
5. Verify user management capabilities

## Security Considerations
- Change default admin password in production
- Implement proper password policies
- Add rate limiting in production
- Use environment variables for sensitive data
- Regular security audits recommended

# MAXX ENERGY RBAC System – Integration & Implementation Notes

## Tools & Libraries Used
- **Python**: Main programming language
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database access
- **Flask-WTF**: Form handling and CSRF protection
- **Werkzeug**: Password hashing utilities
- **MySQL**: (for group project) or SQLite (for local dev)
- **Jinja2**: Templating engine
- **Flask-Session**: (optional, for advanced session management)
- **python-dotenv**: (optional, for environment variable management)

## RBAC System Implementation in Maxx Energy
- **Models**: User, Role, Permission (with many-to-many relationships)
- **Authentication**: Secure login/logout, password hashing
- **Authorization**: Role-based decorators and permission checks
- **Admin Interface**: Manage users, roles, and permissions via web UI
- **Dynamic Navigation**: Menus and dashboard features shown/hidden based on user role/permissions
- **Security**: CSRF protection, session security, SQL injection protection via SQLAlchemy ORM
- **Seeded Users/Roles**: Default users for each role (admin, executive, manager, staff, guest)

## How to Integrate RBAC into Another Group Project (MySQL, SQLAlchemy, Python)

### 1. Understand the Core Components
- Flask app structure (routes, templates, static files)
- Database models: User, Role, Permission
- Authentication and authorization logic
- Role/permission management UI

### 2. Identify the Target Project's Database
- Confirm the use of MySQL and SQLAlchemy
- Check for existing User model or authentication system

### 3. Integrate the Models
- Copy User, Role, and Permission models into the group project's models file
- Merge with existing User model if needed (add role_id, password methods, etc.)
- Ensure SQLAlchemy `db` object is initialized

### 4. Migrate the Database
- Run `db.create_all()` or use Flask-Migrate/Alembic to create new tables in MySQL
- If using Alembic, generate and apply a migration for the new models

### 5. Integrate the Logic
- Copy authentication, login, logout, and role/permission management routes into the group project's Flask app
- Update import paths and references as needed
- Include decorators (like `@admin_required`) and session logic

### 6. Integrate the Templates
- Copy templates (`login.html`, `dashboard.html`, `role_management.html`, etc.) into the group project's `templates` folder
- Adjust template inheritance and navigation to match the group project's layout

### 7. Update Configuration
- Add security and session config to the group project's `app.config`
- Set up environment variables for secrets and database URI as needed

### 8. Test the Integration
- Create test users and roles in the new database
- Log in as different roles and verify permissions and access control
- Check that the UI and navigation adapt to the new project's style

### 9. Collaborate with Your Team
- Communicate about new models and routes
- Document any changes or new requirements for using the RBAC system
- Ensure everyone knows how to manage users, roles, and permissions

### 10. Example Table
| Step | What to Do |
|------|------------|
| 1    | Copy/merge models (`User`, `Role`, `Permission`) |
| 2    | Migrate database (create new tables/fields)      |
| 3    | Copy/merge routes and logic                      |
| 4    | Copy/merge templates and static files            |
| 5    | Update app config and environment variables      |
| 6    | Test all features and permissions                |
| 7    | Document for your team                           |

---

**If you want to use environment variables for secrets and database URI, use `python-dotenv` and a `.env` file.**

**For any questions or further integration help, refer to this notes file or ask your team lead!** 