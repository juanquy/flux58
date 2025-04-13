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
    """Set page background image directly"""
    try:
        # Initialize database
        db = Database()
        print("Database initialized successfully")
        
        # Create a test image if it doesn't exist
        test_image = "img/test-bg.svg"
        static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        image_path = os.path.join(static_folder, test_image)
        
        if not os.path.exists(image_path):
            print(f"Creating test image at {image_path}")
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            with open(image_path, 'w') as f:
                f.write('<svg width="100" height="100"><rect width="100" height="100" style="fill:blue" /></svg>')
        
        # Set page background image
        print(f"Setting page_bg_image = {test_image}")
        db.set_system_setting("page_bg_image", test_image)
        
        # Retrieve the value to confirm
        retrieved_value = db.get_system_setting("page_bg_image")
        print(f"Retrieved page_bg_image = {retrieved_value}")
        
        # Set the keys
        db.set_system_setting("page_bg_color", "#f0f0f0")
        db.set_system_setting("content_bg_color", "#ffffff")
        db.set_system_setting("content_text_color", "#333333")
        
        print("Done! Page background image has been set.")
        print("Please restart your application and navigate to the site.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()