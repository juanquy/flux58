#!/usr/bin/env python3
import os
import sys
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'flux58'
DB_USER = 'flux58_user'
DB_PASS = 'flux58_password'

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
conn.autocommit = True
cursor = conn.cursor()

# Create test user
test_user_id = str(uuid.uuid4())
username = "test"
password = "test123"
email = "test@example.com"
now = datetime.now().isoformat()
role = "user"

# Generate password hash
password_hash = generate_password_hash(password)
print(f"Generated password hash: {password_hash}")

# Delete any existing test user
cursor.execute("DELETE FROM users WHERE username = %s", (username,))
print(f"Deleted any existing test user")

# Insert test user
cursor.execute(
    """INSERT INTO users 
       (id, username, password_hash, email, created_at, role)
       VALUES (%s, %s, %s, %s, %s, %s)""",
    (test_user_id, username, password_hash, email, now, role)
)
print(f"Created test user with ID: {test_user_id}")

# Add credits for test user (5000 credits)
cursor.execute(
    """INSERT INTO credits
       (user_id, total, used)
       VALUES (%s, %s, %s)""",
    (test_user_id, 5000, 0)
)
print(f"Added 5000 credits to test user")

# Add a sample credit transaction for reference
transaction_id = str(uuid.uuid4())
cursor.execute(
    """INSERT INTO credit_transactions
       (id, user_id, amount, timestamp, type, description, status)
       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
    (transaction_id, test_user_id, 5000, now, "initial", "Initial test credits", "completed")
)
print(f"Added credit transaction record")

# Verify user in database
cursor.execute("SELECT id, username, role FROM users WHERE username = %s", (username,))
user = cursor.fetchone()
print(f"\nVerified test user: ID={user[0]}, Username={user[1]}, Role={user[2]}")

# Verify credits
cursor.execute("SELECT user_id, total, used FROM credits WHERE user_id = %s", (test_user_id,))
credits = cursor.fetchone()
print(f"Verified credits: Total={credits[1]}, Used={credits[2]}")

cursor.close()
conn.close()

print("\nTest user setup completed successfully.")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Credits: 5000")