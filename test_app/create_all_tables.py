#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
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

print("Creating all required tables...")

# Users table
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
print("- Users table created")

# Sessions table
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
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("- Sessions table created")

# Credits table
cursor.execute("""
CREATE TABLE IF NOT EXISTS credits (
    user_id TEXT PRIMARY KEY,
    total INTEGER NOT NULL,
    used INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("- Credits table created")

# Credit transactions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS credit_transactions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("- Credit transactions table created")

# Projects table
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("- Projects table created")

# Project assets table
cursor.execute("""
CREATE TABLE IF NOT EXISTS project_assets (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    type TEXT NOT NULL,
    added_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
)
""")
print("- Project assets table created")

# Project timeline table
cursor.execute("""
CREATE TABLE IF NOT EXISTS project_timeline (
    project_id TEXT PRIMARY KEY,
    duration REAL NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    fps_num INTEGER NOT NULL,
    fps_den INTEGER NOT NULL,
    sample_rate INTEGER NOT NULL,
    channels INTEGER NOT NULL,
    channel_layout INTEGER NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
)
""")
print("- Project timeline table created")

# Timeline tracks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS timeline_tracks (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
)
""")
print("- Timeline tracks table created")

# Timeline clips table
cursor.execute("""
CREATE TABLE IF NOT EXISTS timeline_clips (
    id TEXT PRIMARY KEY,
    track_id TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    position REAL NOT NULL,
    duration REAL NOT NULL,
    start_point REAL NOT NULL,
    end_point REAL NOT NULL,
    properties JSONB NOT NULL,
    FOREIGN KEY (track_id) REFERENCES timeline_tracks(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES project_assets(id) ON DELETE CASCADE
)
""")
print("- Timeline clips table created")

# Export jobs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS export_jobs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    output_path TEXT NOT NULL,
    format TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    fps INTEGER NOT NULL,
    video_bitrate TEXT NOT NULL,
    audio_bitrate TEXT NOT NULL,
    start_frame INTEGER NOT NULL,
    end_frame INTEGER,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    progress REAL DEFAULT 0,
    error TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
""")
print("- Export jobs table created")

# System settings table
cursor.execute("""
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
""")
print("- System settings table created")

# System logs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    level TEXT NOT NULL,
    module TEXT NOT NULL,
    message TEXT NOT NULL,
    user_id TEXT,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
)
""")
print("- System logs table created")

print("\nAll tables created successfully")

# Create admin user with a simple password
admin_id = str(uuid.uuid4())
username = "admin"
password = "admin123"
email = "admin@example.com"
now = datetime.now()
role = "admin"

# Generate password hash
password_hash = generate_password_hash(password)
print(f"\nGenerated password hash for admin: {password_hash}")

# Delete any existing admin users
cursor.execute("DELETE FROM users WHERE username = %s", (username,))
print(f"Deleted any existing admin users")

# Insert admin user
cursor.execute(
    "INSERT INTO users (id, username, password_hash, email, created_at, role) VALUES (%s, %s, %s, %s, %s, %s)",
    (admin_id, username, password_hash, email, now, role)
)
print(f"Created admin user with ID: {admin_id}")

# Insert admin credits
cursor.execute(
    "INSERT INTO credits (user_id, total, used) VALUES (%s, %s, %s)",
    (admin_id, 9999, 0)
)
print(f"Added credits for admin user")

# Create a session for the admin user
session_token = str(uuid.uuid4())
expires_at = now + timedelta(days=30)  # Session expires in 30 days

# Insert session
cursor.execute(
    """INSERT INTO sessions 
       (token, user_id, username, created_at, expires_at, last_activity) 
       VALUES (%s, %s, %s, %s, %s, %s)""",
    (session_token, admin_id, username, now, expires_at, now)
)
print(f"Created session for admin user")

# Verify user by fetching from database
cursor.execute("SELECT id, username, role FROM users WHERE username = %s", (username,))
user = cursor.fetchone()
print(f"\nVerified admin user: ID={user[0]}, Username={user[1]}, Role={user[2]}")

# Verify credits by fetching from database
cursor.execute("SELECT user_id, total, used FROM credits WHERE user_id = %s", (admin_id,))
credits = cursor.fetchone()
print(f"Verified admin credits: Total={credits[1]}, Used={credits[2]}")

# Verify session by fetching from database
cursor.execute("SELECT token, user_id, username, expires_at FROM sessions WHERE user_id = %s", (admin_id,))
session = cursor.fetchone()
print(f"Verified admin session: Token={session[0]}, Expires at={session[3]}")

cursor.close()
conn.close()

print("\nSetup completed successfully")
print("To apply these changes, restart the service:")
print("sudo systemctl restart openshot-web.service")
print(f"\nLogin with:")
print(f"Username: {username}")
print(f"Password: {password}")