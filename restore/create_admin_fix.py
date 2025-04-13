#!/usr/bin/env python3

import os
import uuid
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

# Database configuration using postgres user (which we know works)
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'flux58'
DB_USER = 'postgres'
DB_PASS = 'postgres'

print(f"Connecting to database as {DB_USER}")

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

# Create flux58_user if it doesn't exist
try:
    # Check if flux58_user exists
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'flux58_user'")
    if not cursor.fetchone():
        print("Creating flux58_user role...")
        cursor.execute("CREATE USER flux58_user WITH PASSWORD 'flux58_password'")
        print("Created flux58_user role")
    
    # Grant privileges to flux58_user
    cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO flux58_user")
    cursor.execute(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flux58_user")
    cursor.execute(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO flux58_user")
    print("Granted privileges to flux58_user")
except Exception as e:
    print(f"Error setting up flux58_user: {str(e)}")

# Create super admin user with known ID for debugging
admin_id = 'superadmin2'
username = 'superadmin2'
password = 'superadmin2'
email = 'superadmin2@flux58.com'
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