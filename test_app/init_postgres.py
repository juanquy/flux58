#!/usr/bin/env python3
# PostgreSQL database initialization script for OpenShot web app

import os
import psycopg2
import sys
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'flux58_user')
DB_PASS = os.environ.get('DB_PASS', 'flux58_password')

def init_db():
    """Initialize PostgreSQL database with required tables"""
    print(f"Initializing PostgreSQL database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
    
    try:
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
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            role TEXT NOT NULL
        )
        ''')
        
        # Create sessions table
        cursor.execute('''
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
        ''')
        
        # Create projects table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            settings JSONB,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create assets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            metadata JSONB,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
        ''')
        
        # Create clips table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clips (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            track_id INTEGER NOT NULL,
            position FLOAT NOT NULL,
            duration FLOAT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            properties JSONB,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
        )
        ''')
        
        # Create export_jobs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS export_jobs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            output_path TEXT,
            format TEXT NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            fps FLOAT NOT NULL,
            video_bitrate TEXT,
            audio_bitrate TEXT,
            start_frame INTEGER,
            end_frame INTEGER,
            started_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP,
            status TEXT NOT NULL,
            error_message TEXT,
            progress FLOAT DEFAULT 0.0,
            priority INTEGER DEFAULT 0,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create system_settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
        ''')
        
        # Create user_credits table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_credits (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            reference_id TEXT,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create logs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            level TEXT NOT NULL,
            module TEXT,
            message TEXT NOT NULL,
            user_id TEXT,
            ip_address TEXT,
            details JSONB,
            context JSONB
        )
        ''')
        
        # Create admin account if it doesn't exist
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            print("Creating admin account")
            admin_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Create admin user
            cursor.execute(
                """INSERT INTO users 
                   (id, username, password_hash, email, created_at, role)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (admin_id, "admin", generate_password_hash("admin123"), 
                 "admin@flux58.com", now, "admin")
            )
            
            # Add initial credits to admin
            tx_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO user_credits
                   (id, user_id, amount, timestamp, description, type, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (tx_id, admin_id, 9999, now, "Admin account setup", "initial", "completed")
            )
            
            print("Admin account created successfully")
        
        conn.close()
        print("Database initialization completed successfully")
        return True
    
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    init_db()