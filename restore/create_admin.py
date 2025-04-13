#!/usr/bin/env python3

import os
import uuid
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

# Connect directly to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
conn.autocommit = True
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Create super admin user with known ID for debugging
admin_id = 'superadmin'
username = 'superadmin'
password = 'superadmin'
email = 'superadmin@flux58.com'
now = datetime.now()
role = 'admin'

# Generate password hash using Werkzeug
password_hash = generate_password_hash(password)
print(f"Generated password hash: {password_hash}")

try:
    # Delete user if exists
    cursor.execute("DELETE FROM users WHERE username = %s", (username,))
    print(f"Removed any existing user with username '{username}'")
    
    # Create admin user
    cursor.execute(
        """INSERT INTO users 
           (id, username, password_hash, email, created_at, role)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (admin_id, username, password_hash, email, now, role)
    )
    print(f"Created admin user: {username} with role: {role}")
    
    # Add initial credits
    cursor.execute(
        """INSERT INTO credits
           (user_id, total, used)
           VALUES (%s, %s, %s)""",
        (admin_id, 9999, 0)
    )
    print(f"Added credits to user: {username}")
    
    print(f"\nSuperAdmin account created successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
except Exception as e:
    print(f"Error creating admin user: {str(e)}")
finally:
    cursor.close()
    conn.close()