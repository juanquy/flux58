#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def check_settings_table():
    """Check if the system_settings table exists"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'system_settings'
            )
        """)
        
        table_exists = cursor.fetchone()['exists']
        print(f"system_settings table exists: {table_exists}")
        
        if not table_exists:
            return False
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'system_settings'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  {col['column_name']} ({col['data_type']})")
        
        # Count settings
        cursor.execute("SELECT COUNT(*) FROM system_settings")
        count = cursor.fetchone()['count']
        print(f"\nNumber of settings: {count}")
        
        # Get all settings
        cursor.execute("SELECT key, value, updated_at FROM system_settings")
        settings = cursor.fetchall()
        
        print("\nExisting settings:")
        for setting in settings:
            print(f"  {setting['key']} = {setting['value']} (updated: {setting['updated_at']})")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def test_setting_save():
    """Test saving and retrieving a setting"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create test value
        test_key = "test_setting"
        test_value = f"test_value_{os.urandom(4).hex()}"
        
        print(f"\nSaving test setting: {test_key} = {test_value}")
        
        # Try saving
        try:
            cursor.execute(
                "UPDATE system_settings SET value = %s, updated_at = NOW() WHERE key = %s",
                (test_value, test_key)
            )
            
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO system_settings (key, value, updated_at) VALUES (%s, %s, NOW())",
                    (test_key, test_value)
                )
                
            conn.commit()
            print("Setting saved successfully")
        except Exception as e:
            conn.rollback()
            print(f"Error saving setting: {str(e)}")
            return False
        
        # Try retrieving
        try:
            cursor.execute("SELECT value FROM system_settings WHERE key = %s", (test_key,))
            result = cursor.fetchone()
            
            if result and result['value'] == test_value:
                print(f"Setting retrieved successfully: {result['value']}")
                return True
            else:
                print(f"Setting retrieval failed: {result}")
                return False
        except Exception as e:
            print(f"Error retrieving setting: {str(e)}")
            return False
    finally:
        cursor.close()
        conn.close()

def create_settings_table():
    """Create the system_settings table if it doesn't exist"""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key VARCHAR(255) PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)
        
        conn.commit()
        print("Created system_settings table")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error creating table: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Testing PostgreSQL system settings...")
    
    # Check if table exists
    table_exists = check_settings_table()
    
    # Create table if needed
    if not table_exists:
        print("\nTable doesn't exist, creating...")
        if create_settings_table():
            print("Table created, checking again...")
            check_settings_table()
    
    # Test saving and retrieving
    test_setting_save()