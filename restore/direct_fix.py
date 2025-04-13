#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import RealDictCursor
import shutil
import time
import os

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def direct_db_fix():
    """Force reset all landing page settings directly in the database"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # First, check the system_settings table
        cursor.execute("SELECT COUNT(*) FROM system_settings")
        count = cursor.fetchone()['count']
        print(f"Current settings count: {count}")
        
        # Get current DB settings
        cursor.execute("SELECT key, value FROM system_settings")
        current_settings = {row['key']: row['value'] for row in cursor.fetchall()}
        
        # Create a backup file of app.py
        app_py_path = "/root/OpenShot/test_app/app.py"
        backup_path = f"/root/OpenShot/test_app/app.py.landing_fix_backup_{int(time.time())}"
        shutil.copy2(app_py_path, backup_path)
        print(f"Created backup of app.py at {backup_path}")
        
        # Read the app.py file
        with open(app_py_path, 'r') as f:
            app_py_content = f.read()
        
        # Look for the get_landing_page_settings function
        if "def get_landing_page_settings()" in app_py_content:
            print("Found get_landing_page_settings function, modifying it...")
            
            # Find the starting point of the function
            function_start = app_py_content.find("def get_landing_page_settings()")
            
            # Find the start of the next function
            next_function = app_py_content.find("def ", function_start + 10)
            
            # Extract the entire function
            if next_function != -1:
                original_function = app_py_content[function_start:next_function]
            else:
                original_function = app_py_content[function_start:]
            
            # Create the modified function
            modified_function = """def get_landing_page_settings():
    \"\"\"Get landing page settings for templates\"\"\"
    # MODIFIED: This function has been modified to use a direct database lookup 
    # for getting landing page settings
    
    # Default settings
    settings = {
        "navbar": {
            "bg_color": "#212529",
            "brand_text": "FLUX58 AI MEDIA LABS",
            "logo": "img/flux58-logo.png",
            "text_color": "#ffffff",
            "menu_items": []
        },
        "footer": {
            "bg_color": "#212529",
            "copyright_text": "© 2025 FLUX58 AI MEDIA LABS. All rights reserved.",
            "show_social": True
        },
        "hero": {
            "title": "FLUX58 AI MEDIA LABS",
            "subtitle": "Powerful AI-Enhanced Video Editing",
            "text": "Create professional videos with our cloud-based video editor, powered by AI",
            "image": "img/custom/openshot-banner.jpg",
            "bg_color": "#343a40",
            "text_color": "#ffffff",
            "bg_image": "",
            "bg_image_overlay": False
        },
        "features": {
            "title": "Features",
            "accent_color": "#007bff",
            "cards": [
                {
                    "icon": "bi-camera-video",
                    "title": "Video Editing",
                    "text": "Edit video with our powerful cloud-based editor"
                },
                {
                    "icon": "bi-robot",
                    "title": "AI Enhancement",
                    "text": "Leverage AI to enhance your videos automatically"
                },
                {
                    "icon": "bi-cloud-upload",
                    "title": "Cloud Storage",
                    "text": "Store your projects securely in the cloud"
                }
            ]
        },
        "cta": {
            "title": "Ready to get started?",
            "subtitle": "Sign up today and create amazing videos.",
            "button_text": "Get Started",
            "button_color": "#007bff"
        },
        "page": {
            "bg_color": "#ffffff",
            "content_bg_color": "#ffffff",
            "content_text_color": "#212529",
            "bg_image": ""
        }
    }
    
    # IMPORTANT DEBUG - Force showing all settings
    print("DEBUG: ===== RETRIEVING ALL SETTINGS FROM DATABASE =====")
    all_settings = db.get_all_system_settings()
    
    if isinstance(all_settings, dict):
        for key, value in all_settings.items():
            print(f"DEBUG: DB setting: {key} = {value}")
    else:
        print(f"DEBUG: get_all_system_settings() returned non-dict: {type(all_settings)}")
    print("DEBUG: ===== END OF SETTINGS =====")
    
    # Override with database settings
    # Navbar settings
    navbar_bg = db.get_system_setting('navbar_bg_color')
    if navbar_bg:
        settings['navbar']['bg_color'] = navbar_bg
    
    brand_text = db.get_system_setting('navbar_brand_text')
    if brand_text:
        settings['navbar']['brand_text'] = brand_text
    
    logo = db.get_system_setting('navbar_logo')
    if logo:
        settings['navbar']['logo'] = logo
    
    navbar_text_color = db.get_system_setting('navbar_text_color')
    if navbar_text_color:
        settings['navbar']['text_color'] = navbar_text_color
        
    menu_items_json = db.get_system_setting('navbar_menu_items')
    if menu_items_json:
        try:
            import json
            settings['navbar']['menu_items'] = json.loads(menu_items_json)
        except:
            pass
    
    # Hero section settings
    title = db.get_system_setting('landing_page_title')
    if title:
        settings['hero']['title'] = title
        
    subtitle = db.get_system_setting('landing_page_subtitle')
    if subtitle:
        settings['hero']['subtitle'] = subtitle
        
    description = db.get_system_setting('landing_page_description')
    if description:
        settings['hero']['text'] = description
        
    hero_bg_color = db.get_system_setting('hero_bg_color')
    if hero_bg_color:
        settings['hero']['bg_color'] = hero_bg_color
        
    hero_text_color = db.get_system_setting('hero_text_color')
    if hero_text_color:
        settings['hero']['text_color'] = hero_text_color
        
    hero_image = db.get_system_setting('landing_page_hero_image')
    if hero_image:
        settings['hero']['image'] = hero_image
        
    hero_bg_image = db.get_system_setting('hero_bg_image')
    if hero_bg_image:
        settings['hero']['bg_image'] = hero_bg_image
        print("DEBUG: Found hero_bg_image setting:", hero_bg_image)
        
    hero_bg_image_overlay = db.get_system_setting('hero_bg_image_overlay')
    if hero_bg_image_overlay:
        settings['hero']['bg_image_overlay'] = hero_bg_image_overlay == 'True'
    
    # Features section
    features_title = db.get_system_setting('features_title')
    if features_title:
        settings['features']['title'] = features_title
        
    features_accent_color = db.get_system_setting('features_accent_color')
    if features_accent_color:
        settings['features']['accent_color'] = features_accent_color
        
    # Feature cards
    for i in range(3):
        feature_icon = db.get_system_setting(f'feature{i+1}_icon')
        feature_title = db.get_system_setting(f'feature{i+1}_title')
        feature_text = db.get_system_setting(f'feature{i+1}_text')
        
        if feature_icon:
            settings['features']['cards'][i]['icon'] = feature_icon
        if feature_title:
            settings['features']['cards'][i]['title'] = feature_title
        if feature_text:
            settings['features']['cards'][i]['text'] = feature_text
    
    # Page settings
    page_bg_color = db.get_system_setting('page_bg_color')
    if page_bg_color:
        settings['page']['bg_color'] = page_bg_color
        
    content_bg_color = db.get_system_setting('content_bg_color')
    if content_bg_color:
        settings['page']['content_bg_color'] = content_bg_color
        
    content_text_color = db.get_system_setting('content_text_color')
    if content_text_color:
        settings['page']['content_text_color'] = content_text_color
        
    # Page background image - IMPORTANT: THIS SECTION WAS BUGGY
    page_bg_image = db.get_system_setting('page_bg_image')
    if page_bg_image:
        settings['page']['bg_image'] = page_bg_image
        print("DEBUG: Found page_bg_image setting:", page_bg_image)
    
    # CTA section
    cta_title = db.get_system_setting('cta_title')
    if cta_title:
        settings['cta']['title'] = cta_title
        
    cta_subtitle = db.get_system_setting('cta_subtitle')
    if cta_subtitle:
        settings['cta']['subtitle'] = cta_subtitle
        
    cta_button_text = db.get_system_setting('cta_button_text')
    if cta_button_text:
        settings['cta']['button_text'] = cta_button_text
        
    cta_button_color = db.get_system_setting('cta_button_color')
    if cta_button_color:
        settings['cta']['button_color'] = cta_button_color
    
    # Print out the final settings for debugging
    print("FINAL SETTINGS BEING RETURNED:")
    print(f"  Page BG Image: {settings['page'].get('bg_image', 'None')}")
    print(f"  Page BG Color: {settings['page'].get('bg_color', 'None')}")
    
    return settings
"""
            # Replace the function in the file
            new_app_py_content = app_py_content.replace(original_function, modified_function)
            
            # Save the new app.py
            with open(app_py_path, 'w') as f:
                f.write(new_app_py_content)
            
            print("Successfully modified the get_landing_page_settings function!")
        else:
            print("Error: Could not find get_landing_page_settings function in app.py")
        
        # Create direct fix to ensure database is PostgreSQL
        pg_fix = """
# DIRECT FIX: Reset the Database instance to ensure PostgreSQL is used
try:
    from database import Database
    from postgres_db import PostgresDatabase
    import os
    
    # Get database parameters from environment
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', '5432'))
    DB_NAME = os.environ.get('DB_NAME', 'flux58')
    DB_USER = os.environ.get('DB_USER', 'flux58_user')
    DB_PASS = os.environ.get('DB_PASS', 'flux58_password')
    
    # Create new database instance
    db = Database(host=DB_HOST, port=DB_PORT, 
                  database=DB_NAME, user=DB_USER, password=DB_PASS)
    
    # Force environment variables
    os.environ['DB_TYPE'] = 'postgres'
    os.environ['DB_HOST'] = DB_HOST
    os.environ['DB_PORT'] = str(DB_PORT)
    os.environ['DB_NAME'] = DB_NAME
    os.environ['DB_USER'] = DB_USER
    os.environ['DB_PASS'] = DB_PASS
    
    print("DIRECT FIX: Forced PostgreSQL database connection")
    
    # Test connection with a simple query
    test_setting = db.get_system_setting('test_fix_direct', 'not_set')
    db.set_system_setting('test_fix_direct', 'SUCCESS')
    print(f"DIRECT FIX: Database test: {test_setting} -> SUCCESS")
except Exception as e:
    print(f"DIRECT FIX ERROR: {str(e)}")

"""
        # Find a good place to add the direct fix
        # After the app is created but before routes are defined
        app_creation_pos = app_py_content.find("app = Flask(__name__)")
        if app_creation_pos != -1:
            import_section_end = app_py_content.find("\n\n", app_creation_pos)
            if import_section_end != -1:
                new_app_py_content = app_py_content[:import_section_end+2] + pg_fix + app_py_content[import_section_end+2:]
                
                # Save the modified file
                with open(app_py_path, 'w') as f:
                    f.write(new_app_py_content)
                    
                print("Successfully added direct PostgreSQL fix to app.py")
            else:
                print("Error: Could not find appropriate insertion point after app creation")
        else:
            print("Error: Could not find app creation in app.py")
        
        # Set proper PostgreSQL environment variables for flux58.py
        flux58_py_path = "/root/OpenShot/test_app/flux58.py"
        with open(flux58_py_path, 'r') as f:
            flux58_content = f.read()
            
        # Ensure PostgreSQL environment variables are forced
        env_var_section = """
# Force environment variables for database
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'
"""
        # Check if environment variables are already set
        if "os.environ['DB_TYPE'] = 'postgres'" in flux58_content:
            print("Environment variables already set in flux58.py")
        else:
            # Find a good place to insert the environment variables
            import_section = flux58_content.find("import")
            if import_section != -1:
                next_import_end = flux58_content.find("\n\n", import_section)
                if next_import_end != -1:
                    new_flux58_content = flux58_content[:next_import_end+2] + env_var_section + flux58_content[next_import_end+2:]
                    
                    # Save the modified file
                    with open(flux58_py_path, 'w') as f:
                        f.write(new_flux58_content)
                        
                    print("Successfully added PostgreSQL environment variables to flux58.py")
                else:
                    print("Error: Could not find appropriate insertion point after imports")
            else:
                print("Error: Could not find imports in flux58.py")
        
        print("\nImplemented direct fixes to app.py and flux58.py. The landing page settings should now work correctly.")
        print("Please run 'python flux58.py' to test the changes.")
        
        return True
    except Exception as e:
        print(f"Error implementing direct fix: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Implementing direct fix for landing page settings...")
    direct_db_fix()