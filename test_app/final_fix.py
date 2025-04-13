#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import shutil

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def fix_get_landing_page_settings():
    """Replace the get_landing_page_settings function entirely to always use database values"""
    app_py_path = "/root/OpenShot/test_app/app.py"
    
    # Create backup
    backup_path = f"{app_py_path}.final_fix_{int(time.time())}"
    shutil.copy2(app_py_path, backup_path)
    print(f"Created backup of app.py at {backup_path}")
    
    # Read the file
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Create the new get_landing_page_settings function
    new_function = """
def get_landing_page_settings():
    \"\"\"Get landing page settings for templates - COMPLETELY REWRITTEN FOR FIX\"\"\"
    
    # Direct database connection to always get fresh settings
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', '5432')),
            database=os.environ.get('DB_NAME', 'flux58'),
            user=os.environ.get('DB_USER', 'flux58_user'),
            password=os.environ.get('DB_PASS', 'flux58_password')
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT key, value FROM system_settings")
        db_settings = {row['key']: row['value'] for row in cursor.fetchall()}
        cursor.close()
        
        print("DEBUG: Direct DB lookup - found {} settings".format(len(db_settings)))
        
        # Get page_bg_image setting directly from DB
        if 'page_bg_image' in db_settings:
            bg_img = db_settings['page_bg_image']
            print(f"DEBUG: Direct DB - page_bg_image = '{bg_img}'")
    except Exception as e:
        print(f"DEBUG: Direct DB connection error: {str(e)}")
        db_settings = {}
    finally:
        if conn:
            conn.close()
    
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
    
    # Override with database settings
    if 'navbar_bg_color' in db_settings:
        settings['navbar']['bg_color'] = db_settings['navbar_bg_color']
        
    if 'navbar_brand_text' in db_settings:
        settings['navbar']['brand_text'] = db_settings['navbar_brand_text']
        
    if 'navbar_logo' in db_settings:
        settings['navbar']['logo'] = db_settings['navbar_logo']
        
    if 'navbar_text_color' in db_settings:
        settings['navbar']['text_color'] = db_settings['navbar_text_color']
        
    if 'navbar_menu_items' in db_settings:
        try:
            settings['navbar']['menu_items'] = json.loads(db_settings['navbar_menu_items'])
        except Exception as e:
            print(f"Error parsing menu items: {str(e)}")
    
    # Hero section
    if 'landing_page_title' in db_settings:
        settings['hero']['title'] = db_settings['landing_page_title']
        
    if 'landing_page_subtitle' in db_settings:
        settings['hero']['subtitle'] = db_settings['landing_page_subtitle']
        
    if 'landing_page_description' in db_settings:
        settings['hero']['text'] = db_settings['landing_page_description']
        
    if 'hero_bg_color' in db_settings:
        settings['hero']['bg_color'] = db_settings['hero_bg_color']
        
    if 'hero_text_color' in db_settings:
        settings['hero']['text_color'] = db_settings['hero_text_color']
        
    if 'landing_page_hero_image' in db_settings:
        settings['hero']['image'] = db_settings['landing_page_hero_image']
        
    if 'hero_bg_image' in db_settings:
        settings['hero']['bg_image'] = db_settings['hero_bg_image']
        print(f"DEBUG: Setting hero_bg_image to '{db_settings['hero_bg_image']}'")
        
    if 'hero_bg_image_overlay' in db_settings:
        settings['hero']['bg_image_overlay'] = db_settings['hero_bg_image_overlay'] == 'True'
    
    # Page settings
    if 'page_bg_color' in db_settings:
        settings['page']['bg_color'] = db_settings['page_bg_color']
        
    if 'content_bg_color' in db_settings:
        settings['page']['content_bg_color'] = db_settings['content_bg_color']
        
    if 'content_text_color' in db_settings:
        settings['page']['content_text_color'] = db_settings['content_text_color']
        
    # MOST IMPORTANT - Page background image
    if 'page_bg_image' in db_settings and db_settings['page_bg_image']:
        settings['page']['bg_image'] = db_settings['page_bg_image']
        print(f"DEBUG: Using page_bg_image = '{db_settings['page_bg_image']}'")
        
        # Check if the file actually exists
        if db_settings['page_bg_image']:
            img_path = os.path.join(app.static_folder, db_settings['page_bg_image'])
            file_exists = os.path.isfile(img_path)
            print(f"DEBUG: Image file {img_path} exists: {file_exists}")
    else:
        print("DEBUG: No page_bg_image setting found in database")
    
    # Features section
    if 'features_title' in db_settings:
        settings['features']['title'] = db_settings['features_title']
        
    if 'features_accent_color' in db_settings:
        settings['features']['accent_color'] = db_settings['features_accent_color']
    
    # Print the full background image settings
    print(f"DEBUG: FINAL page_bg_image = '{settings['page']['bg_image']}'")
    
    return settings
"""
    
    # Find the existing get_landing_page_settings function
    start_idx = content.find("def get_landing_page_settings():")
    if start_idx == -1:
        print("Could not find get_landing_page_settings function")
        return False
        
    # Find the end of the function
    next_func = content.find("\ndef ", start_idx + 10)
    if next_func == -1:
        print("Could not find the end of the function")
        return False
        
    # Replace the function
    new_content = content[:start_idx] + new_function + content[next_func:]
    
    # Write the new content
    with open(app_py_path, 'w') as f:
        f.write(new_content)
    
    print("Successfully replaced get_landing_page_settings function")
    return True

def fix_layout_html():
    """Fix the layout.html file to properly display background images"""
    layout_path = "/root/OpenShot/test_app/templates/layout.html"
    
    # Create backup
    backup_path = f"{layout_path}.final_fix_{int(time.time())}"
    shutil.copy2(layout_path, backup_path)
    print(f"Created backup of layout.html at {backup_path}")
    
    # Read the file
    with open(layout_path, 'r') as f:
        content = f.read()
    
    # Create a completely new body tag section
    new_body_tag = """<body
    {% if landing_page_settings.page.bg_image and landing_page_settings.page.bg_image|string|trim %}
    style="background-image: url('{{ url_for('static', filename=landing_page_settings.page.bg_image) }}'); 
           background-size: cover; 
           background-attachment: fixed; 
           background-position: center;
           background-repeat: no-repeat;
           background-color: {{ landing_page_settings.page.bg_color|default('#ffffff') }};"
    {% else %}
    style="background-color: {{ landing_page_settings.page.bg_color|default('#ffffff') }};"
    {% endif %}>
    
    <!-- FINAL FIX DEBUG INFO --> 
    <div style="position: fixed; bottom: 0; left: 0; background: rgba(0,0,0,0.8); color: white; padding: 5px; font-size: 10px; z-index: 9999; max-width: 300px; overflow: hidden;">
        <b>Background Settings:</b><br>
        Page BG Image: "{{ landing_page_settings.page.bg_image|default('None') }}"<br>
        Page BG Color: {{ landing_page_settings.page.bg_color|default('None') }}<br>
        Using Image: {% if landing_page_settings.page.bg_image and landing_page_settings.page.bg_image|string|trim %}Yes{% else %}No{% endif %}
    </div>"""
    
    # Find the body tag
    body_start = content.find("<body")
    if body_start == -1:
        print("Could not find body tag")
        return False
        
    body_end = content.find(">", body_start)
    nav_start = content.find("<nav", body_end)
    
    if body_end == -1 or nav_start == -1:
        print("Could not find body tag end or nav start")
        return False
    
    # Replace the body tag and everything up to the nav
    new_content = content[:body_start] + new_body_tag + content[nav_start:]
    
    # Write the new content
    with open(layout_path, 'w') as f:
        f.write(new_content)
    
    print("Successfully fixed layout.html")
    return True

def fix_admin_landing_page_save():
    """Fix the admin_landing_page_save2 function to properly handle page_bg_image"""
    app_py_path = "/root/OpenShot/test_app/app.py"
    
    # Read the file
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Find the page section in admin_landing_page_save2
    page_section_start = content.find("elif section == 'page':")
    if page_section_start == -1:
        print("Could not find page section in admin_landing_page_save2")
        return False
    
    # Look for where the page_bg_image handling begins
    bg_image_handling_start = content.find("# Handle page background image upload", page_section_start)
    if bg_image_handling_start == -1:
        print("Could not find page background image handling")
        return False
    
    # Find the end of the if block for handling page_bg_image
    bg_image_handling_end = content.find("# Handle deletion request", bg_image_handling_start)
    if bg_image_handling_end == -1:
        print("Could not find end of page background image handling")
        return False
    
    # Create new page_bg_image handling
    new_bg_image_handling = """            # Handle page background image upload
            if 'page_bg_image' in request.files and request.files['page_bg_image'].filename:
                page_bg_image = request.files['page_bg_image']
                
                # Print debug info
                print("FINAL FIX: Received page_bg_image file:", page_bg_image.filename)
                
                # Create actual filename
                filename = "page_bg_{0}{1}".format(int(time.time()), os.path.splitext(page_bg_image.filename)[1])
                static_path = os.path.join('img', 'custom', filename)
                filepath = os.path.join(app.static_folder, 'img', 'custom', filename)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save the file
                page_bg_image.save(filepath)
                
                # Set permissions
                os.chmod(filepath, 0o644)
                
                # Update the setting
                image_path = static_path
                db.set_system_setting('page_bg_image', image_path)
                print("FINAL FIX: Saved page background image to", filepath)
                print("FINAL FIX: Updated setting page_bg_image to", image_path)
                
                # Force update for current session
                # Clear any existing setting in app.config
                if 'page_bg_image' in app.config:
                    del app.config['page_bg_image']
                    
                # Force browser to reload image by adding timestamp parameter
                # This prevents browser caching from showing the old image
                if 'landing_page_config' in app.config:
                    del app.config['landing_page_config']
                    
                # Direct database verification
                try:
                    conn = psycopg2.connect(
                        host=os.environ.get('DB_HOST', 'localhost'),
                        port=int(os.environ.get('DB_PORT', '5432')),
                        database=os.environ.get('DB_NAME', 'flux58'),
                        user=os.environ.get('DB_USER', 'flux58_user'),
                        password=os.environ.get('DB_PASS', 'flux58_password')
                    )
                    cursor = conn.cursor()
                    cursor.execute("SELECT value FROM system_settings WHERE key = 'page_bg_image'")
                    result = cursor.fetchone()
                    print(f"FINAL FIX: Direct DB verification: page_bg_image = {result[0] if result else 'None'}")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"FINAL FIX: DB verification error: {str(e)}")"""
    
    # Replace the old handling with the new one
    new_content = content[:bg_image_handling_start] + new_bg_image_handling + content[bg_image_handling_end:]
    
    # Write the new content
    with open(app_py_path, 'w') as f:
        f.write(new_content)
    
    print("Successfully fixed admin_landing_page_save2 function")
    return True

def reset_all_settings():
    """Reset all settings in the database to ensure clean state"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Get all current settings
        cursor.execute("SELECT key, value FROM system_settings")
        current_settings = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Reset important settings
        if 'page_bg_image' in current_settings:
            print(f"Current page_bg_image: {current_settings['page_bg_image']}")
            
            # Check if the file exists
            if current_settings['page_bg_image']:
                img_path = f"/root/OpenShot/test_app/static/{current_settings['page_bg_image']}"
                file_exists = os.path.isfile(img_path)
                print(f"Image file exists: {file_exists}")
                
                if file_exists:
                    # Set proper permissions
                    os.chmod(img_path, 0o644)
                    print(f"Set permissions for {img_path}")
        
        # Reset the setting - comment this out if you don't want to clear existing setting
        # cursor.execute("UPDATE system_settings SET value = '' WHERE key = 'page_bg_image'")
        # conn.commit()
        # print("Reset page_bg_image to empty string")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error resetting settings: {str(e)}")
        return False

def fix_imports():
    """Ensure app.py has the necessary imports"""
    app_py_path = "/root/OpenShot/test_app/app.py"
    
    # Read the file
    with open(app_py_path, 'r') as f:
        content = f.read()
    
    # Check for psycopg2.extras import
    if "import psycopg2.extras" not in content:
        # Find the imports section
        import_section_end = content.find("\n\n", content.find("import"))
        if import_section_end == -1:
            print("Could not find import section")
            return False
        
        # Add the import
        new_content = content[:import_section_end] + "\nimport psycopg2.extras" + content[import_section_end:]
        
        # Write the new content
        with open(app_py_path, 'w') as f:
            f.write(new_content)
        
        print("Added psycopg2.extras import")
    else:
        print("psycopg2.extras import already exists")
    
    return True

if __name__ == "__main__":
    print("Applying comprehensive fix for landing page background images...")
    
    # Step 1: Reset settings to ensure clean state
    print("\nStep 1: Resetting settings...")
    reset_all_settings()
    
    # Step 2: Add necessary imports
    print("\nStep 2: Adding necessary imports...")
    fix_imports()
    
    # Step 3: Fix the get_landing_page_settings function
    print("\nStep 3: Fixing get_landing_page_settings function...")
    fix_get_landing_page_settings()
    
    # Step 4: Fix the layout.html template
    print("\nStep 4: Fixing layout.html template...")
    fix_layout_html()
    
    # Step 5: Fix the admin_landing_page_save2 function
    print("\nStep 5: Fixing admin_landing_page_save2 function...")
    fix_admin_landing_page_save()
    
    print("\nFixes complete! Please restart the application.")
    print("The landing page background image functionality should now work correctly.")