#!/usr/bin/env python3

import os
from database import Database
from werkzeug.security import generate_password_hash

# Database configuration
DB_TYPE = 'postgres'  # Use PostgreSQL
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

# Initialize our database
db = Database(use_postgres=True, host=DB_HOST, port=DB_PORT, 
              database=DB_NAME, user=DB_USER, password=DB_PASS)

def reset_user_password(username, new_password):
    """Reset a user's password"""
    # Get user from database
    user = db.get_user_by_username(username)
    
    if not user:
        print(f"User '{username}' not found in database")
        return False
    
    # Generate new password hash
    password_hash = generate_password_hash(new_password)
    
    # Update user
    result = db.update_user(user['id'], password_hash=password_hash)
    
    if result:
        print(f"Password for user '{username}' has been reset")
        return True
    else:
        print(f"Failed to reset password for user '{username}'")
        return False

if __name__ == "__main__":
    # Reset admin password
    reset_user_password('admin', 'admin123')
    
    # Optionally reset test user password
    # reset_user_password('test', 'test123')