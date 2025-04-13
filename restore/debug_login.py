#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import uuid
import os
from werkzeug.security import generate_password_hash, check_password_hash

print("Starting login debugging script")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="flux58",
        user="postgres",
        password="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("Connected to PostgreSQL database")
except Exception as e:
    print(f"ERROR connecting to database: {str(e)}")
    exit(1)

# Check if admin user exists and verify password hash
try:
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()
    
    if admin:
        print(f"Admin user found: {admin['id']}, Role: {admin['role']}")
        
        # Verify the password hash for admin123
        test_password = "admin123"
        password_valid = check_password_hash(admin['password_hash'], test_password)
        print(f"Admin password hash: {admin['password_hash']}")
        print(f"Password valid for 'admin123': {password_valid}")
        
        if not password_valid:
            print("Updating admin password to 'admin123'")
            password_hash = generate_password_hash("admin123")
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'admin'",
                (password_hash,)
            )
            print("Password updated successfully")
    else:
        print("Admin user not found in database")
except Exception as e:
    print(f"ERROR checking admin user: {str(e)}")

# Check for test user
try:
    cursor.execute("SELECT * FROM users WHERE username = 'test'")
    test_user = cursor.fetchone()
    
    if test_user:
        print(f"Test user found: {test_user['id']}, Role: {test_user['role']}")
        
        # Verify the password hash for test123
        test_password = "test123"
        password_valid = check_password_hash(test_user['password_hash'], test_password)
        print(f"Test password hash: {test_user['password_hash']}")
        print(f"Password valid for 'test123': {password_valid}")
        
        if not password_valid:
            print("Updating test password to 'test123'")
            password_hash = generate_password_hash("test123")
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = 'test'",
                (password_hash,)
            )
            print("Password updated successfully")
    else:
        print("Test user not found in database")
except Exception as e:
    print(f"ERROR checking test user: {str(e)}")

# Check sessions table
try:
    cursor.execute("SELECT COUNT(*) as count FROM sessions")
    session_count = cursor.fetchone()['count']
    print(f"Number of sessions in database: {session_count}")
    
    cursor.execute("SELECT * FROM sessions LIMIT 5")
    sessions = cursor.fetchall()
    for session in sessions:
        print(f"Session: {session['token'][:8]}... User: {session['username']}, Expires: {session['expires_at']}")
except Exception as e:
    print(f"ERROR checking sessions: {str(e)}")

# Check Flask session configuration in app.py
print("\nChecking Flask session configuration...")
try:
    with open('/home/juanquy/OpenShot/test_app/app.py', 'r') as f:
        app_code = f.read()
        
    if "app.secret_key" in app_code:
        print("app.secret_key is configured in app.py")
    else:
        print("WARNING: app.secret_key not found in app.py")
        
    if "app.config['SESSION_TYPE']" in app_code:
        print("Session type is configured in app.py")
    else:
        print("INFO: Default Flask session type (client-side with cookies) is used")
        
    if "session.permanent" in app_code:
        print("Session permanence is configured in app.py")
    else:
        print("INFO: Session permanence is not explicitly set")
except Exception as e:
    print(f"ERROR checking app.py: {str(e)}")

print("\nExamining login route...")
try:
    # Check for login_page function
    with open('/home/juanquy/OpenShot/test_app/app.py', 'r') as f:
        app_code = f.read()
    
    if "@app.route('/login'" in app_code:
        print("Login route found in app.py")
    else:
        print("WARNING: Login route not found in app.py")
        
    if "def login_page" in app_code:
        print("login_page function found in app.py")
    else:
        print("WARNING: login_page function not found in app.py")
    
    if "redirect(url_for('admin_dashboard'))" in app_code:
        print("Admin redirect found in login code")
    else:
        print("WARNING: Admin redirect not found in login code")
        
    if "redirect(url_for('dashboard'))" in app_code:
        print("User redirect found in login code")
    else:
        print("WARNING: User redirect not found in login code")
except Exception as e:
    print(f"ERROR examining login route: {str(e)}")

print("\nChecking for admin_dashboard and dashboard routes...")
try:
    with open('/home/juanquy/OpenShot/test_app/app.py', 'r') as f:
        app_code = f.read()
    
    if "@app.route('/admin')" in app_code:
        print("Admin dashboard route found in app.py")
    else:
        print("WARNING: Admin dashboard route not found in app.py")
        
    if "def admin_dashboard" in app_code:
        print("admin_dashboard function found in app.py")
    else:
        print("WARNING: admin_dashboard function not found in app.py")
        
    if "@app.route('/dashboard')" in app_code:
        print("User dashboard route found in app.py")
    else:
        print("WARNING: User dashboard route not found in app.py")
        
    if "def dashboard" in app_code:
        print("dashboard function found in app.py")
    else:
        print("WARNING: dashboard function not found in app.py")
except Exception as e:
    print(f"ERROR checking dashboard routes: {str(e)}")

# Create a test fix for the routes if needed
print("\nChecking for @admin_required decorator...")
try:
    with open('/home/juanquy/OpenShot/test_app/app.py', 'r') as f:
        app_code = f.read()
    
    if "def admin_required" in app_code:
        print("admin_required decorator found in app.py")
    else:
        print("WARNING: admin_required decorator not found in app.py")
except Exception as e:
    print(f"ERROR checking admin_required decorator: {str(e)}")

# Close database connection
cursor.close()
conn.close()

print("\nDebugging completed. Run the following to fix environment variables in the service file:")
print("sudo systemctl stop openshot-web.service")
print("sudo cp /home/juanquy/OpenShot/test_app/openshot-web-fixed.service /etc/systemd/system/openshot-web.service")
print("sudo systemctl daemon-reload")
print("sudo systemctl start openshot-web.service")
print("sudo systemctl status openshot-web.service")