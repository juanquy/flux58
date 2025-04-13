#!/usr/bin/env python3
import os
import shutil
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import re

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'flux58',
    'user': 'flux58_user',
    'password': 'flux58_password'
}

def find_render_template_in_app():
    """Fix the home route to ensure it uses the current settings"""
    app_py_path = "/root/OpenShot/test_app/app.py"
    
    # Create backup
    backup_path = f"/root/OpenShot/test_app/app.py.page_rendering_fix_{int(time.time())}"
    shutil.copy2(app_py_path, backup_path)
    print(f"Created backup of app.py at {backup_path}")
    
    # Read the app.py file
    with open(app_py_path, 'r') as f:
        app_content = f.read()
    
    # Find the home route
    home_route_match = re.search(r'@app\.route\([\'\']/[\'\']\)\s*def\s+home\(\):.*?return\s+render_template.*?index\.html.*?', app_content, re.DOTALL)
    
    if home_route_match:
        home_route = home_route_match.group(0)
        print("Found home route:")
        print(home_route)
        
        # Create a modified version to ensure it always gets fresh settings
        if "get_landing_page_settings()" in home_route:
            print("Home route already uses get_landing_page_settings()")
        else:
            # Create modified home route
            modified_home_route = '''@app.route('/')
def home():
    """Home page"""
    # Get landing page settings
    landing_page = get_landing_page_settings()
    
    # Print debug info about landing page settings
    print("DEBUG: Rendering home page with settings:")
    print(f"  Page BG Image: {landing_page['page'].get('bg_image', 'None')}")
    print(f"  Page BG Color: {landing_page['page'].get('bg_color', 'None')}")
    
    # Pass settings to template
    return render_template('index.html', landing_page_settings=landing_page)
'''
            # Replace the original home route
            new_app_content = app_content.replace(home_route, modified_home_route)
            
            # Save the changes
            with open(app_py_path, 'w') as f:
                f.write(new_app_content)
                
            print("Successfully modified home route to use get_landing_page_settings()")
    else:
        print("Could not find home route in app.py")
    
    # Now check the render_template function for other issues
    template_render_calls = re.findall(r'return\s+render_template\([\'"]([^\'"]*)[\'"](.*?)\)', app_content)
    
    print("\nFound template render calls:")
    for template, args in template_render_calls:
        print(f"  {template}: {args}")
        
        # Check if landing_page_settings is passed to the template
        if "landing_page_settings" not in args and template != "index.html":
            print(f"WARNING: Template {template} does not include landing_page_settings")
    
    # Fix the layout.html template to ensure it works with bg_image
    layout_html_path = "/root/OpenShot/test_app/templates/layout.html"
    
    # Create backup
    layout_backup = f"/root/OpenShot/test_app/templates/layout.html.backup_{int(time.time())}"
    shutil.copy2(layout_html_path, layout_backup)
    
    # Read the layout file
    with open(layout_html_path, 'r') as f:
        layout_content = f.read()
    
    # Check for background image conditions
    if "landing_page_settings.page.bg_image" in layout_content:
        print("\nFound background image condition in layout.html")
        
        # Fix the condition to make sure it uses the correct images
        bg_image_block = re.search(r'<body[^>]*?{% if landing_page_settings\.page\.bg_image %}.*?{% else %}.*?{% endif %}', layout_content, re.DOTALL)
        
        if bg_image_block:
            body_tag = bg_image_block.group(0)
            print("Found body tag with bg_image condition")
            
            # Extract debug div if present
            debug_div = ""
            debug_match = re.search(r'{% if landing_page_settings\.page\.bg_image %}.*?<div style="position: fixed.*?</div>.*?{% endif %}', layout_content, re.DOTALL)
            if debug_match:
                debug_div = debug_match.group(0)
                print("Found debug div")
            
            # Create a new modified body tag with improved background detection
            modified_body_tag = '''<body
    {% if landing_page_settings.page.bg_image and landing_page_settings.page.bg_image|trim %}
    style="background-image: url('{{ url_for('static', filename=landing_page_settings.page.bg_image) }}'); 
           background-size: cover; 
           background-attachment: fixed; 
           background-position: center;
           background-color: {{ landing_page_settings.page.bg_color|default('#ffffff') }};
           background-blend-mode: soft-light;"
    {% else %}
    style="background-color: {{ landing_page_settings.page.bg_color|default('#ffffff') }};"
    {% endif %}>
    
    <!-- MODIFIED DEBUG INFO - REMOVE IN PRODUCTION -->
    <div style="position: fixed; bottom: 0; right: 0; background: rgba(0,0,0,0.7); color: white; padding: 5px; font-size: 10px; z-index: 9999;">
        Background Image: {{ landing_page_settings.page.bg_image|default('None') }}<br>
        Background Color: {{ landing_page_settings.page.bg_color|default('None') }}
    </div>'''
            
            # Replace the original body tag
            new_layout_content = layout_content.replace(body_tag, modified_body_tag)
            
            # Save the changes
            with open(layout_html_path, 'w') as f:
                f.write(new_layout_content)
                
            print("Successfully modified layout.html to improve background image handling")
        else:
            print("Could not find body tag with bg_image condition in layout.html")
    else:
        print("Could not find background image condition in layout.html")

def check_database_settings():
    """Check the page_bg_image setting in the database"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the page_bg_image setting
        cursor.execute("SELECT key, value, updated_at FROM system_settings WHERE key = 'page_bg_image'")
        setting = cursor.fetchone()
        
        if setting:
            print(f"\nCurrent page_bg_image setting: {setting['value']} (updated: {setting['updated_at']})")
            
            # Check if the image file exists
            image_path = setting['value']
            if image_path and image_path.strip():
                full_path = f"/root/OpenShot/test_app/static/{image_path}"
                if os.path.exists(full_path):
                    print(f"Image file exists: {full_path}")
                    
                    # Fix permissions
                    os.chmod(full_path, 0o644)
                    print("Fixed image file permissions to 644")
                else:
                    print(f"WARNING: Image file does not exist: {full_path}")
        else:
            print("\nNo page_bg_image setting found in the database")
        
        return True
    except Exception as e:
        print(f"Error checking database settings: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Fixing page rendering for background images...")
    
    # Check database settings
    check_database_settings()
    
    # Fix render_template usage
    find_render_template_in_app()
    
    print("\nFixes applied. Please restart the application to see the changes.")