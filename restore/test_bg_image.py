#!/usr/bin/env python3
import os
import psycopg2
import time
import shutil
from werkzeug.security import generate_password_hash

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def reset_page_bg_image():
    """Reset the page_bg_image setting in the database for testing"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Check current value
        cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
        result = cursor.fetchone()
        current_value = result[0] if result else "None"
        print(f"Current page_bg_image: {current_value}")
        
        # Reset the value to empty string
        cursor.execute("UPDATE system_settings SET value = '' WHERE key = 'page_bg_image'")
        conn.commit()
        print("Reset page_bg_image to empty string")
        
        # Verify the change
        cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
        result = cursor.fetchone()
        new_value = result[0] if result else "None"
        print(f"New page_bg_image: {new_value}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error resetting page_bg_image: {str(e)}")
        if conn:
            conn.close()
        return False

def set_test_bg_image():
    """Set a test background image path for testing"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Set the background image to a test value
        test_image_path = "img/custom/test_bg_image.jpg"
        cursor.execute("UPDATE system_settings SET value = %s WHERE key = 'page_bg_image'", (test_image_path,))
        conn.commit()
        print(f"Set page_bg_image to: {test_image_path}")
        
        # Verify the change
        cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
        result = cursor.fetchone()
        new_value = result[0] if result else "None"
        print(f"New page_bg_image: {new_value}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error setting test page_bg_image: {str(e)}")
        if conn:
            conn.close()
        return False

def create_test_image():
    """Create a test background image file"""
    try:
        # Ensure the custom directory exists
        static_path = "/root/OpenShot/test_app/static"
        custom_dir = os.path.join(static_path, "img", "custom")
        os.makedirs(custom_dir, exist_ok=True)
        
        # Create or copy a test image
        test_image_path = os.path.join(custom_dir, "test_bg_image.jpg")
        
        # If the hero image exists, copy it as our test background
        hero_image_path = os.path.join(static_path, "img", "hero-image.jpg")
        if os.path.exists(hero_image_path):
            shutil.copy2(hero_image_path, test_image_path)
            print(f"Copied hero image to: {test_image_path}")
        else:
            # Create an empty file as fallback
            with open(test_image_path, "w") as f:
                f.write("Test image file")
            print(f"Created dummy test image: {test_image_path}")
        
        # Set proper permissions
        os.chmod(test_image_path, 0o644)
        print(f"Set permissions for {test_image_path}")
        
        return True
    except Exception as e:
        print(f"Error creating test image: {str(e)}")
        return False

def test_get_bg_image():
    """Test direct database query for background image"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Get the page_bg_image setting
        cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
        result = cursor.fetchone()
        bg_image = result[0] if result else "None"
        print(f"Direct query - page_bg_image: {bg_image}")
        
        conn.close()
        return bg_image
    except Exception as e:
        print(f"Error getting page_bg_image: {str(e)}")
        if conn:
            conn.close()
        return None

def verify_file_exists(image_path):
    """Verify if the image file exists in static folder"""
    if not image_path:
        print("No image path provided")
        return False
        
    full_path = os.path.join("/root/OpenShot/test_app/static", image_path)
    exists = os.path.isfile(full_path)
    if exists:
        # Get file permissions
        permissions = oct(os.stat(full_path).st_mode & 0o777)
        size = os.path.getsize(full_path)
        print(f"File {full_path} exists: {exists}, permissions: {permissions}, size: {size} bytes")
    else:
        print(f"File {full_path} does not exist")
    
    return exists

def run_all_tests():
    """Run all tests in sequence"""
    print("=== RUNNING BACKGROUND IMAGE TESTS ===")
    
    # Reset the setting
    print("\n1. Resetting page_bg_image setting...")
    reset_page_bg_image()
    
    # Create test image
    print("\n2. Creating test background image...")
    create_test_image()
    
    # Verify the image exists
    print("\n3. Verifying test image exists...")
    verify_file_exists("img/custom/test_bg_image.jpg")
    
    # Set the test image path in database
    print("\n4. Setting page_bg_image in database...")
    set_test_bg_image()
    
    # Test direct database query
    print("\n5. Testing direct database query...")
    bg_image = test_get_bg_image()
    
    # Verify the image path in database matches the file on disk
    print("\n6. Final verification...")
    if bg_image:
        verify_file_exists(bg_image)
    
    print("\n=== BACKGROUND IMAGE TESTS COMPLETE ===")

if __name__ == "__main__":
    run_all_tests()