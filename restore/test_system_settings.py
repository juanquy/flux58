#!/usr/bin/env python3
import os
import sys
import time

# Force environment variables for database
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'

# Import the database module
from database import Database

def main():
    """Test system settings functionality"""
    try:
        # Initialize database
        db = Database()
        print("Database initialized successfully")
        
        # Test setting and retrieving a simple value
        test_key = "test_key_" + str(int(time.time()))
        test_value = "test_value_" + str(int(time.time()))
        
        print(f"Setting {test_key} = {test_value}")
        result = db.set_system_setting(test_key, test_value)
        print(f"Result: {result}")
        
        # Retrieve the value
        retrieved_value = db.get_system_setting(test_key)
        print(f"Retrieved {test_key} = {retrieved_value}")
        
        # Set and get page background image
        page_bg_image = "img/custom/test-bg-" + str(int(time.time())) + ".svg"
        print(f"Setting page_bg_image = {page_bg_image}")
        result = db.set_system_setting("page_bg_image", page_bg_image)
        print(f"Result: {result}")
        
        # Retrieve the value
        retrieved_value = db.get_system_setting("page_bg_image")
        print(f"Retrieved page_bg_image = {retrieved_value}")
        
        # Get all settings
        all_settings = db.get_all_system_settings()
        print("All settings:")
        for key, value in all_settings.items():
            print(f"  {key} = {value}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()