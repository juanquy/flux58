#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from datetime import datetime
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

# Create users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    role TEXT NOT NULL
)
""")

# Create credits table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS credits (
    user_id TEXT PRIMARY KEY,
    total INTEGER NOT NULL,
    used INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

print("Tables created successfully")

# Create admin user with simple password
admin_id = str(uuid.uuid4())
username = "admin"
password = "admin123"
email = "admin@example.com"
created_at = datetime.now().isoformat()
role = "admin"

# Generate password hash with a simple, standard format
password_hash = generate_password_hash(password)
print(f"Generated password hash: {password_hash}")

# Delete any existing admin users
cursor.execute("DELETE FROM users WHERE username = %s", (username,))
print(f"Deleted any existing admin users")

# Insert admin user
cursor.execute(
    "INSERT INTO users (id, username, password_hash, email, created_at, role) VALUES (%s, %s, %s, %s, %s, %s)",
    (admin_id, username, password_hash, email, created_at, role)
)
print(f"Created admin user with ID: {admin_id}")

# Insert admin credits
cursor.execute(
    "INSERT INTO credits (user_id, total, used) VALUES (%s, %s, %s)",
    (admin_id, 9999, 0)
)
print(f"Added credits for admin user")

# Create the service file that uses postgres credentials
service_file = """[Unit]
Description=OpenShot Web Service
After=network.target postgresql.service

[Service]
User=juanquy
WorkingDirectory=/home/juanquy/OpenShot/test_app
ExecStart=/home/juanquy/openshot_service_venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=on-failure
Environment="FLASK_ENV=production"
Environment="DB_TYPE=postgres"
Environment="DB_HOST=localhost" 
Environment="DB_PORT=5432"
Environment="DB_NAME=flux58"
Environment="DB_USER=postgres"
Environment="DB_PASS=postgres"

[Install]
WantedBy=multi-user.target
"""

with open('/home/juanquy/OpenShot/test_app/openshot-web-fixed.service', 'w') as f:
    f.write(service_file)

print("Created service file with postgres credentials")
print("\nSetup completed. To apply the changes, run:")
print("sudo cp /home/juanquy/OpenShot/test_app/openshot-web-fixed.service /etc/systemd/system/openshot-web.service && sudo systemctl daemon-reload && sudo systemctl start openshot-web.service")
print("\nThen login with:")
print(f"Username: {username}")
print(f"Password: {password}")

cursor.close()
conn.close()