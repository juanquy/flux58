#!/usr/bin/env python3
import os
import sys
import requests
import re
from urllib.parse import urlparse

# Target URL
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/login"
ADMIN_URL = f"{BASE_URL}/admin"
USERNAME = "admin"
PASSWORD = "admin123"

# Session for maintaining cookies
session = requests.Session()

# Step 1: Login
print("Step 1: Logging in...")
login_data = {
    "username": USERNAME,
    "password": PASSWORD
}

response = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
print(f"Status code: {response.status_code}")
print(f"URL after login: {response.url}")
print(f"Cookies after login: {session.cookies.get_dict()}")

# Step 2: Access admin dashboard
print("\nStep 2: Accessing admin dashboard...")
response = session.get(ADMIN_URL)
print(f"Status code: {response.status_code}")
print(f"URL: {response.url}")

# Print a summary of the response content to check if admin page is loading
print("\nAdmin page response content preview (first 500 chars):")
preview = response.text[:500] if len(response.text) > 500 else response.text
print(preview)

# Step 3: Check if we can access admin_dashboard directly
print("\nStep 3: Trying to access admin_dashboard directly...")
admin_dashboard_url = f"{BASE_URL}/admin/dashboard"
response = session.get(admin_dashboard_url)
print(f"Status code: {response.status_code}")
print(f"URL: {response.url}")

print("\nAdmin dashboard response content preview (first 500 chars):")
preview = response.text[:500] if len(response.text) > 500 else response.text
print(preview)

# Step 4: Check database for role and permissions
print("\nStep 4: Checking database for role and permissions...")
import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="flux58",
        user="postgres",
        password="postgres"
    )
    cursor = conn.cursor()
    
    # Get the admin user
    cursor.execute("SELECT id, username, role, created_at FROM users WHERE username = %s", (USERNAME,))
    user = cursor.fetchone()
    
    if user:
        user_id = user[0]
        role = user[2]
        created_at = user[3]
        print(f"Found user: ID={user_id}, Username={user[1]}, Role={role}, Created at={created_at}")
        
        # Try to update the role to ensure it's correct
        cursor.execute("UPDATE users SET role = 'admin' WHERE id = %s", (user_id,))
        conn.commit()
        print(f"Updated role to 'admin' for user {user_id}")
    else:
        print(f"User '{USERNAME}' not found in database")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error checking database: {e}")

print("\nAdmin debugging completed")