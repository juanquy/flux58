#!/usr/bin/env python3
import os
import time
import psycopg2
from datetime import datetime

# Set environment variables for database
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'

# Import the database module
from database import Database, DemoDatabase

def check_which_db_is_used():
    """Check which database implementation is actually being used"""
    print("Testing database implementation...")
    
    # Create a database instance
    db = Database(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT')),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS')
    )
    
    # Generate a unique test key and value
    test_key = f"test_db_impl_{int(time.time())}"
    test_value = f"test_value_{datetime.now().isoformat()}"
    
    print(f"Setting test value: {test_key} = {test_value}")
    
    # Try to set a test value in the database
    db.set_system_setting(test_key, test_value)
    
    # Retrieve the value from PostgreSQL directly
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        port=int(os.environ.get('DB_PORT')),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS')
    )
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key = %s", (test_key,))
    pg_value = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # Retrieve the value using the Database instance
    db_value = db.get_system_setting(test_key)
    
    print(f"\nResults:")
    print(f"  Value from PostgreSQL: {pg_value[0] if pg_value else None}")
    print(f"  Value from Database instance: {db_value}")
    
    # Check if the values match
    if pg_value and pg_value[0] == db_value:
        print("\nSUCCESS: Database instance is using PostgreSQL")
        return True
    else:
        print("\nWARNING: Database instance might NOT be using PostgreSQL")
        print(f"  PostgreSQL type: {type(pg_value)}")
        print(f"  Database type: {type(db_value)}")
        
        # Check if we're using DemoDatabase
        print(f"\nChecking if using DemoDatabase...")
        print(f"  db.use_postgres: {getattr(db, 'use_postgres', 'attribute not found')}")
        print(f"  db.pg_db type: {type(getattr(db, 'pg_db', None))}")
        
        if hasattr(db, 'pg_db') and isinstance(db.pg_db, DemoDatabase):
            print("PROBLEM: Database is using DemoDatabase instead of PostgreSQL!")
        
        return False

if __name__ == "__main__":
    check_which_db_is_used()