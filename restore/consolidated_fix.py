#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import shutil
import re

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def backup_file(file_path):
    """Create a backup of a file before modifying it"""
    backup_path = f"{file_path}.backup_{int(time.time())}"
    shutil.copy2(file_path, backup_path)
    print(f"Created backup at {backup_path}")
    return backup_path

def fix_app_py():
    """Fix app.py to properly initialize project_manager"""
    app_py_path = "/root/OpenShot/test_app/app.py"
    
    # Create backup
    backup_file(app_py_path)
    
    # Read the file
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Fix project_manager initialization
    pattern1 = r"# Try to initialize Postgres database\s+db = Database\(host=DB_HOST, port=DB_PORT, \s+database=DB_NAME, user=DB_USER, password=DB_PASS\)\s+print\(\"Using PostgreSQL database: \{\} on \{\}:\{\}\"\\.format\(DB_NAME, DB_HOST, DB_PORT\)\)"
    replacement1 = """# Try to initialize Postgres database
    db = Database(host=DB_HOST, port=DB_PORT, 
                  database=DB_NAME, user=DB_USER, password=DB_PASS)
    print("Using PostgreSQL database: {} on {}:{}".format(DB_NAME, DB_HOST, DB_PORT))
    
    # Import projects module and set db
    import projects
    projects.db = db
    
    # Initialize project manager with proper base_path
    project_manager = ProjectManager(base_path=DATA_DIR)
    print("Initializing OpenShot library...")"""
    
    # Apply first replacement
    content = re.sub(pattern1, replacement1, content)
    
    # Fix demo database fallback
    pattern2 = r"# Use demo database\s+db = DemoDatabase\(\)\s+print\(\"Using in-memory database for testing\"\)"
    replacement2 = """# Use demo database
    db = DemoDatabase()
    print("Using in-memory database for testing")
    
    # Create demo project manager for fallback
    project_manager = ProjectManager(base_path=DATA_DIR)
    print("Using demo project manager for testing")"""
    
    # Apply second replacement
    content = re.sub(pattern2, replacement2, content)
    
    # Add psycopg2.extras import if not already there
    if "import psycopg2.extras" not in content:
        import_section_end = content.find("\n\n", content.find("import"))
        if import_section_end != -1:
            content = content[:import_section_end] + "\nimport psycopg2.extras" + content[import_section_end:]
    
    # Write the updated content
    with open(app_py_path, 'w') as f:
        f.write(content)
    
    print("Successfully updated app.py with project_manager initialization")
    return True

def fix_layout_html():
    """Fix references to 'navbar' in layout.html to use 'landing_page_settings.navbar'"""
    layout_path = "/root/OpenShot/test_app/templates/layout.html"
    
    # Create backup
    backup_file(layout_path)
    
    # Read the file
    with open(layout_path, 'r') as f:
        content = f.read()
    
    # Fix navbar references
    content = content.replace('{{ navbar.bg_color|default', '{{ landing_page_settings.navbar.bg_color|default')
    content = content.replace('{{ navbar.logo|default', '{{ landing_page_settings.navbar.logo|default')
    content = content.replace('{{ navbar.brand_text|default', '{{ landing_page_settings.navbar.brand_text|default')
    content = content.replace('{% for item in navbar.get', '{% for item in landing_page_settings.navbar.get')
    content = content.replace('{{ navbar.text_color|default', '{{ landing_page_settings.navbar.text_color|default')
    
    # Write the updated content
    with open(layout_path, 'w') as f:
        f.write(content)
    
    print("Successfully updated layout.html with correct navbar references")
    return True

def ensure_custom_directories():
    """Create necessary directories for image storage with proper permissions"""
    static_path = "/root/OpenShot/test_app/static"
    custom_img_dir = os.path.join(static_path, "img", "custom")
    
    # Create directory if it doesn't exist
    if not os.path.exists(custom_img_dir):
        os.makedirs(custom_img_dir, exist_ok=True)
        print(f"Created directory: {custom_img_dir}")
    
    # Set proper permissions
    os.chmod(custom_img_dir, 0o755)
    print(f"Set permissions for {custom_img_dir}")
    
    # Check existing images and fix permissions
    for filename in os.listdir(custom_img_dir):
        file_path = os.path.join(custom_img_dir, filename)
        if os.path.isfile(file_path):
            os.chmod(file_path, 0o644)
            print(f"Set permissions for {file_path}")
    
    return True

def verify_settings():
    """Verify database settings for background images"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Get the page_bg_image setting
        cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
        result = cursor.fetchone()
        bg_image = result[0] if result else "None"
        print(f"Verification - page_bg_image: {bg_image}")
        
        # Check if the file exists
        if bg_image and bg_image != "None" and bg_image.strip():
            file_path = os.path.join("/root/OpenShot/test_app/static", bg_image)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_perms = oct(os.stat(file_path).st_mode & 0o777)
                print(f"File exists: {file_path} (size: {file_size} bytes, permissions: {file_perms})")
            else:
                print(f"Warning: File does not exist: {file_path}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error verifying settings: {str(e)}")
        if conn:
            conn.close()
        return False

def create_test_image():
    """Create a test background image in case none exists"""
    try:
        # Ensure the custom directory exists
        static_path = "/root/OpenShot/test_app/static"
        custom_dir = os.path.join(static_path, "img", "custom")
        os.makedirs(custom_dir, exist_ok=True)
        
        # Create or copy a test image
        test_image_path = os.path.join(custom_dir, "test_bg_image.jpg")
        
        # Check if the test image already exists
        if os.path.exists(test_image_path):
            print(f"Test image already exists: {test_image_path}")
            os.chmod(test_image_path, 0o644)
            return True
        
        # If the hero image exists, copy it as our test background
        hero_image_path = os.path.join(static_path, "img", "hero-image.jpg")
        if os.path.exists(hero_image_path):
            shutil.copy2(hero_image_path, test_image_path)
            print(f"Created test image: {test_image_path}")
        else:
            # Create an empty file as fallback
            with open(test_image_path, "w") as f:
                f.write("Test image file")
            print(f"Created dummy test image: {test_image_path}")
        
        # Set proper permissions
        os.chmod(test_image_path, 0o644)
        print(f"Set permissions for {test_image_path}")
        
        # Update the database setting
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Get current value
        cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
        result = cursor.fetchone()
        current_value = result[0] if result else None
        
        # Only update if empty
        if not current_value or current_value.strip() == '':
            test_image_rel_path = os.path.join("img", "custom", "test_bg_image.jpg")
            cursor.execute(
                "UPDATE system_settings SET value = %s WHERE key = 'page_bg_image'", 
                (test_image_rel_path,)
            )
            conn.commit()
            print(f"Updated page_bg_image in database to: {test_image_rel_path}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating test image: {str(e)}")
        return False

def run_all_fixes():
    """Run all fixes in sequence"""
    print("\n=== RUNNING CONSOLIDATED FIXES ===\n")
    
    print("1. Fixing app.py...")
    fix_app_py()
    
    print("\n2. Fixing layout.html...")
    fix_layout_html()
    
    print("\n3. Ensuring custom directories exist with proper permissions...")
    ensure_custom_directories()
    
    print("\n4. Creating test background image (if needed)...")
    create_test_image()
    
    print("\n5. Verifying database settings...")
    verify_settings()
    
    print("\n=== ALL FIXES COMPLETE ===")
    print("\nThe landing page background image functionality should now work correctly.")
    print("Try uploading and updating background images through the admin interface at:")
    print("  http://[server-ip]:5090/admin/landing_page")
    print("\nUse these credentials to login:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == "__main__":
    run_all_fixes()