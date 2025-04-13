#!/usr/bin/env python3
import os
import sys
import uuid
import time
from datetime import datetime
import logging

# Force environment variables for database
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'

# Set a persistent secret key
os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_for_testing_only'

# Add detailed logging
logging.basicConfig(level=logging.DEBUG)

# Import the Flask app - use correct path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Check PostgreSQL connection
try:
    import psycopg2
    print("PostgreSQL module loaded successfully")
    
    # Test database connection
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT')),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS')
    )
    conn.close()
    print("PostgreSQL connection successful")
except Exception as e:
    print(f"Database connection error: {str(e)}")
    sys.exit(1)

# Import the Database class
try:
    from database import Database
    
    # Create a test database instance to ensure PostgreSQL is working
    db_test = Database(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT')),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS')
    )
    
    # Test setting a value
    test_key = f"flux58_startup_{int(time.time())}"
    db_test.set_system_setting(test_key, "STARTUP_TEST")
    
    # Verify the value was set
    value = db_test.get_system_setting(test_key)
    if value == "STARTUP_TEST":
        print("Database test successful - PostgreSQL is working properly")
    else:
        print(f"WARNING: Database test failed - expected 'STARTUP_TEST', got '{value}'")
except Exception as e:
    print(f"Database test error: {str(e)}")
    sys.exit(1)

# Clear any cached modules to ensure a fresh app start
for module in list(sys.modules.keys()):
    if module.startswith('app'):
        del sys.modules[module]

# Import the app
print("Importing app.py with properly configured environment...")
from app import app

# Display environment variables for verification
print(f"\nEnvironment variables:")
print(f"  DB_TYPE: {os.environ.get('DB_TYPE')}")
print(f"  DB_HOST: {os.environ.get('DB_HOST')}")
print(f"  DB_PORT: {os.environ.get('DB_PORT')}")
print(f"  DB_NAME: {os.environ.get('DB_NAME')}")
print(f"  DB_USER: {os.environ.get('DB_USER')}")

# Ensure we're using the PostgreSQL database
from app import db
try:
    # Check if db.pg_db exists and is the right type
    if hasattr(db, 'pg_db'):
        from postgres_db import PostgresDatabase
        if isinstance(db.pg_db, PostgresDatabase):
            print("\nCONFIRMED: app.db is using PostgresDatabase implementation")
        else:
            print(f"\nWARNING: app.db.pg_db is not PostgresDatabase: {type(db.pg_db)}")
    else:
        print("\nWARNING: app.db does not have a pg_db attribute")
except Exception as e:
    print(f"\nError checking db implementation: {str(e)}")

def check_port_in_use(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if __name__ == '__main__':
    # Set port to 5090
    port = 5090
    
    # Check if port is already in use
    if check_port_in_use(port):
        print(f"ERROR: Port {port} is already in use")
        sys.exit(1)
    
    print(f"Starting server on port {port}...")
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)