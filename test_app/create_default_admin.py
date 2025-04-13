#!/usr/bin/env python3
"""
Create a default admin user during installation, ensuring
the admin user can log in the first time the application is run.
"""

import os
import sys
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

# Define admin user credentials
DEFAULT_ADMIN_ID = str(uuid.uuid4())
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"
DEFAULT_EMAIL = "admin@example.com"
DEFAULT_ROLE = "admin"

try:
    # First try connecting with the application's database module
    print("Trying to use flux58_app database module...")
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from flux58_app import Database, create_admin_user
        
        # Initialize database
        db = Database(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', '5432')),
            database=os.environ.get('DB_NAME', 'flux58'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASS', 'postgres')
        )
        
        # Create admin user via the application's function
        result = create_admin_user(
            db=db,
            username=DEFAULT_USERNAME,
            password=DEFAULT_PASSWORD, 
            email=DEFAULT_EMAIL
        )
        
        if result:
            print("Default admin user created successfully using app module")
            print(f"Username: {DEFAULT_USERNAME}")
            print(f"Password: {DEFAULT_PASSWORD}")
            sys.exit(0)
        else:
            print("Failed to create admin user using app module, trying direct database connection...")
    except ImportError as e:
        print(f"Could not import from flux58_app: {e}")
        print("Trying direct database connection...")
    
    # If app module approach failed, try direct database connection
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    # Database configuration - try to use postgres credentials which should have full permissions
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', '5432'))
    DB_NAME = os.environ.get('DB_NAME', 'flux58')
    DB_USER = 'postgres'  # Use postgres superuser
    DB_PASS = 'postgres'
    
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = True
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if admin user already exists
    print(f"Checking if user '{DEFAULT_USERNAME}' already exists...")
    cursor.execute("SELECT * FROM users WHERE username = %s", (DEFAULT_USERNAME,))
    if cursor.fetchone():
        print(f"Admin user '{DEFAULT_USERNAME}' already exists.")
        sys.exit(0)
    
    # Generate password hash
    password_hash = generate_password_hash(DEFAULT_PASSWORD)
    now = datetime.now()
    
    print(f"Creating admin user: {DEFAULT_USERNAME}")
    
    # Create admin user
    cursor.execute(
        """INSERT INTO users 
            (id, username, password_hash, email, created_at, role)
            VALUES (%s, %s, %s, %s, %s, %s)""",
        (DEFAULT_ADMIN_ID, DEFAULT_USERNAME, password_hash, DEFAULT_EMAIL, now, DEFAULT_ROLE)
    )
    
    # Add initial credits
    print(f"Adding initial credits for {DEFAULT_USERNAME}")
    cursor.execute(
        "INSERT INTO credits (user_id, total, used) VALUES (%s, %s, %s)",
        (DEFAULT_ADMIN_ID, 1000, 0)
    )
    
    print(f"Default admin user created successfully via direct database connection")
    print(f"Username: {DEFAULT_USERNAME}")
    print(f"Password: {DEFAULT_PASSWORD}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error creating default admin user: {str(e)}")
    sys.exit(1)