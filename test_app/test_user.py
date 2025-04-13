#!/usr/bin/env python3

import os
from database import Database
from werkzeug.security import check_password_hash, generate_password_hash

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

# Initialize our database
db = Database(use_postgres=True, host=DB_HOST, port=DB_PORT, 
              database=DB_NAME, user=DB_USER, password=DB_PASS)

# Testing admin1 user
user = db.get_user_by_username('admin1')
if user:
    print(f"User found: {user['username']} with role: {user['role']}")
    
    # Add test for password - admin1 should have password 'admin1'
    if check_password_hash(user['password_hash'], 'admin1'):
        print("Password for 'admin1' is correct")
    else:
        print("Password for 'admin1' does not match 'admin1'")
        # Generate correct hash for admin1 password
        correct_hash = generate_password_hash('admin1')
        print(f"Correct hash would be: {correct_hash}")
        
        # Update the password
        db.update_user(user['id'], password_hash=correct_hash)
        print("Updated admin1 password")
else:
    print("User 'admin1' not found")