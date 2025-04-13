#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import uuid
import os

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="flux58",
    user="postgres",
    password="postgres"
)
conn.autocommit = True
cursor = conn.cursor()

# Create sessions table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    last_activity TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

print("Sessions table created successfully")

# Get admin user from database
cursor.execute("SELECT id, username FROM users WHERE username = 'admin'")
admin = cursor.fetchone()

if admin:
    admin_id = admin[0]
    username = admin[1]
    
    # Delete any existing sessions for this user
    cursor.execute("DELETE FROM sessions WHERE user_id = %s", (admin_id,))
    print(f"Deleted any existing sessions for admin user")
    
    # Create a new session token
    token = str(uuid.uuid4())
    now = datetime.now()
    expires_at = now + timedelta(days=7)  # Session expires in 7 days
    
    # Insert session
    cursor.execute(
        """INSERT INTO sessions 
           (token, user_id, username, created_at, expires_at, last_activity) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (token, admin_id, username, now, expires_at, now)
    )
    print(f"Created new session for admin user")
    print(f"Session token: {token}")
    print(f"Expires at: {expires_at}")
else:
    print("Admin user not found. Please run setup_admin.py first.")

cursor.close()
conn.close()

print("\nPLEASE RESTART THE SERVICE to apply these changes:")
print("sudo systemctl restart openshot-web.service")