# MAXX ENERGY RBAC System – Development Summary (W3D2)

## 1. Roles and User Accounts

**Seeded User Accounts:**
| Username   | Password  | Role      | Description                |
|------------|-----------|-----------|----------------------------|
| admin      | password  | admin     | Full system control        |
| executive  | password  | executive | High-level access          |
| manager    | password  | manager   | Team/managerial access     |
| staff      | password  | staff     | Standard user access       |
| guest      | password  | guest     | Minimal, home-page only    |

**Role Hierarchy (Most to Least Privilege):**
1. **Admin** – Full control (manage users, roles, permissions, assign permissions, view/edit all content)
2. **Executive** – High-level access (view reports, some management, but not system/user/role management)
3. **Manager** – Can manage their team, view reports, and access relevant features
4. **Staff** – Can view and edit content, access standard features
5. **Guest** – Can only access the home page, no management or dashboard access

---

## 2. Permissions

**System Permissions:**
- `manage_users`: Can manage system users
- `manage_roles`: Can manage roles
- `manage_permissions`: Can manage permissions
- `edit_content`: Can edit content
- `view_content`: Can view content
- `manage_team`: Can manage their team (for managers)
- `view_reports`: Can view reports

**Permissions are assigned to roles by the admin via the role management interface.**

---

## 3. Login and Access Control

- **Login Page:** All users log in with their username and password.
- **Dashboard:** Only admin, executive, manager, and staff can access the dashboard. Guest users are redirected to the home page.
- **Home Page:** Only accessible to guests (or users not logged in). Shows a welcome message and a login link.
- **Role Management & Assign Permissions:** Only admin can access these features.
- **Navigation/Menu:** The dashboard and navigation bar show different options depending on the user’s role and permissions.

---

## 4. Security and Configuration

- **Session Security:** Session cookies are set to be secure, HTTPOnly, and use the Lax SameSite policy.
- **CSRF Protection:** Enabled for all forms.
- **Password Hashing:** All passwords are securely hashed.
- **SQL Injection Protection:** All database access uses SQLAlchemy ORM, which is safe from SQL injection.
- **Input Validation:** (Optional, not applied) – You can add server-side validation for usernames, roles, and permissions.

---

## 5. How to Test

- Use the provided usernames and passwords to log in as each role.
- Admin can manage users, roles, and permissions.
- Executive, manager, and staff see only the features their permissions allow.
- Guest can only see the home page and cannot access any management or dashboard features.

---

## 6. How to Add/Change Permissions

- Log in as admin.
- Go to Role Management or Assign Permissions.
- Assign or remove permissions for any role as needed.

---

**If you need to add more users, just use the admin interface.  
If you want to change what each role can do, update their permissions in the admin panel.**
