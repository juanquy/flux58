#!/usr/bin/env python3
"""
Test PostgreSQL connection and configuration for OpenShot Web App
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("Error: psycopg2 module not found. Please install with 'pip install psycopg2-binary'")
    sys.exit(1)

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

def test_connection():
    """Test the PostgreSQL connection"""
    print(f"Testing PostgreSQL connection to {DB_NAME} on {DB_HOST}:{DB_PORT}")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        
        # Create a cursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Execute a test query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()['version']
        
        print(f"Connection successful!")
        print(f"PostgreSQL version: {version}")
        
        # Check if the database is empty
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cursor.fetchone()['count']
        
        if table_count == 0:
            print("Database appears to be empty. The application will initialize it on first run.")
        else:
            print(f"Database contains {table_count} tables.")
            
            # List the tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = [row['table_name'] for row in cursor.fetchall()]
            print(f"Tables: {', '.join(tables)}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        
        # Check if database doesn't exist
        if "does not exist" in str(e):
            print("\nThe database doesn't exist. You need to create it first:")
            print(f"  1. Connect to PostgreSQL: sudo -u postgres psql")
            print(f"  2. Create the database: CREATE DATABASE {DB_NAME};")
            print(f"  3. Exit PostgreSQL: \\q")
            print("\nAlternatively, update the DB_NAME environment variable to use an existing database.")
        
        # Check if authentication failed
        elif "password authentication failed" in str(e):
            print("\nAuthentication failed. Check your username and password:")
            print(f"  - Current username: {DB_USER}")
            print(f"  - Update DB_USER and DB_PASS environment variables if needed")
        
        # Check if server is not running
        elif "could not connect to server" in str(e):
            print("\nCould not connect to PostgreSQL server. Check that PostgreSQL is running:")
            print(f"  - sudo systemctl status postgresql")
            print(f"  - If not running: sudo systemctl start postgresql")
            print(f"  - Check host and port: {DB_HOST}:{DB_PORT}")
        
        return False

if __name__ == "__main__":
    if test_connection():
        print("\nPostgreSQL configuration appears to be correct.")
        print("You can start the application with PostgreSQL using:")
        print("  DB_TYPE=postgres python app.py")
    else:
        print("\nPlease fix the PostgreSQL configuration before using it with the application.")
        print("You can still use SQLite by setting DB_TYPE=sqlite or omitting the DB_TYPE variable.")
        sys.exit(1)