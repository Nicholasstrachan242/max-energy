# Deploying MAXX ENERGY RBAC System to a Public Server with MySQL & SSH

This guide provides instructions for transferring your RBAC system (currently using SQLite) to a public server with MySQL, including remote SSH setup and best practices.

## 1. Prepare Your Public Server

- **Provision a server** (e.g., AWS EC2, DigitalOcean Droplet, Linode, etc.).
- **Install required packages** on the server:
  - Python 3.x
  - `pip`
  - MySQL server (or use a managed MySQL service)
  - `mysqlclient` or `pymysql` (for Python-MySQL integration)
  - Git (for code deployment)
- **Set up a secure user** for SSH access (disable root login, use SSH keys).

---

## 2. Install MySQL and Create a Database

1.  **Install MySQL** (if not using a managed service):
    ```bash
    sudo apt update
    sudo apt install mysql-server
    ```
2.  **Secure your MySQL installation**:
    ```bash
    sudo mysql_secure_installation
    ```
3.  **Log in to MySQL and create a database and user**:
    ```sql
    CREATE DATABASE maxxenergy_rbac CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER 'rbacuser'@'localhost' IDENTIFIED BY 'your_strong_password';
    GRANT ALL PRIVILEGES ON maxxenergy_rbac.* TO 'rbacuser'@'localhost';
    FLUSH PRIVILEGES;
    ```
    *Note: Using `'localhost'` is more secure if your Flask app and database are on the same server.*

---

## 3. Update Your Flask App for MySQL

1.  **Install the MySQL driver** in your project's virtual environment:
    ```bash
    pip install mysqlclient
    # Or, if you prefer a pure Python driver:
    # pip install PyMySQL
    ```
2.  **Update your `app.py` or `config.py`**:
    - **Important:** Use environment variables for sensitive data. Do not hardcode credentials.
    ```python
    import os

    # For mysqlclient
    db_uri = os.environ.get('DATABASE_URL', 'mysql://user:pass@host/db')
    # For PyMySQL
    # db_uri = os.environ.get('DATABASE_URL', 'mysql+pymysql://user:pass@host/db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    ```
3.  **Set a fixed `SECRET_KEY`** for production (do not use a random one):
    ```python
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-for-dev')
    ```

---

## 4. Database Migration

- **If starting with a fresh database:**
    - On your server, run your app with the new MySQL URI and let SQLAlchemy create the tables. It's best to do this from a Flask shell or a dedicated script.
    ```bash
    flask shell
    >>> from db import db
    >>> db.create_all()
    >>> exit()
    ```
- **If migrating existing data from SQLite to MySQL:**
    - This is a more complex task. You can use a library like **Flask-Migrate** to manage schema changes or export/import data manually.
    - **Manual Migration Steps:**
        1. Export each table from your SQLite database to a CSV file.
        2. Transfer the CSV files to your server.
        3. Use MySQL's `LOAD DATA INFILE` command or a tool like MySQL Workbench to import the data.

---

## 5. Deploy Your Code

1.  **Use Git to clone your repository** onto the server (recommended).
2.  **Set up a Python virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file** in your project root to store environment variables:
    ```
    DATABASE_URL='mysql://rbacuser:your_strong_password@localhost/maxxenergy_rbac'
    SECRET_KEY='a-very-long-and-random-secret-key-for-production'
    ```
4.  **Ensure your app loads these variables** (e.g., using `python-dotenv`).

---

## 6. Configure SSH for Remote Access

1.  **Generate SSH keys** on your local machine if you don't have them:
    ```bash
    ssh-keygen -t rsa -b 4096
    ```
2.  **Copy your public key to the server** for passwordless login:
    ```bash
    ssh-copy-id your_user@your_server_ip
    ```
3.  **Connect securely to your server**:
    ```bash
    ssh your_user@your_server_ip
    ```

---

## 7. Run the App in Production

- **Do not use the built-in Flask development server for production.**
- Use a production-ready WSGI server like **Gunicorn** or **uWSGI**, and run it behind a reverse proxy like **Nginx**.

1.  **Install Gunicorn**:
    ```bash
    pip install gunicorn
    ```
2.  **Run your app with Gunicorn**:
    ```bash
    gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
    ```
    *This makes the app available on port 8000.*

3.  **Set up Nginx** to act as a reverse proxy, forwarding requests from port 80 (HTTP) and 443 (HTTPS) to Gunicorn on port 8000.

---

## 8. Security & Best Practices

- **Never expose your MySQL port (3306) to the public internet.** Use firewall rules (`ufw`) to block it.
- **Use a strong, unique password** for your database user.
- **Change all default passwords**, including the `admin` user in your application.
- **Configure HTTPS** on Nginx using Let's Encrypt for free SSL certificates.
- **Regularly back up your database.**
- **Keep your server and all software dependencies up to date.**

---

## 9. References

- [Flask Deployment Options](https://flask.palletsprojects.com/en/latest/deploying/)
- [Flask-SQLAlchemy MySQL Configuration](https://flask-sqlalchemy.palletsprojects.com/en/latest/config/#mysql)
- [DigitalOcean Guide: How To Serve Flask Applications with Gunicorn and Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04) 