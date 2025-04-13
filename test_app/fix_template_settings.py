#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

print("Starting Template Fix Script")

# 1. Backup app.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

# 2. Read the current app.py file
with open(app_path, 'r') as f:
    content = f.read()

# 3. Find a location to add the landing page settings function
# Look for the last import
last_import_pos = content.rfind("import ")
line_end = content.find("\n", last_import_pos)

# Add template functions just after the imports
template_functions = '''
# Template helper functions
def get_landing_page_settings():
    """Get landing page settings for templates"""
    # Default settings
    settings = {
        "navbar": {
            "bg_color": "#212529",
            "brand_text": "FLUX58 AI MEDIA LABS",
            "logo": "img/flux58-logo.png"
        },
        "footer": {
            "bg_color": "#212529",
            "copyright_text": "© 2025 FLUX58 AI MEDIA LABS. All rights reserved.",
            "show_social": True
        }
    }
    
    # Override with database settings if available
    try:
        # Get settings from database
        navbar_bg = db.get_system_setting('navbar_bg_color')
        if navbar_bg:
            settings['navbar']['bg_color'] = navbar_bg
        
        brand_text = db.get_system_setting('navbar_brand_text')
        if brand_text:
            settings['navbar']['brand_text'] = brand_text
        
        logo = db.get_system_setting('navbar_logo')
        if logo:
            settings['navbar']['logo'] = logo
        
        footer_bg = db.get_system_setting('footer_bg_color')
        if footer_bg:
            settings['footer']['bg_color'] = footer_bg
        
        copyright_text = db.get_system_setting('footer_copyright_text')
        if copyright_text:
            settings['footer']['copyright_text'] = copyright_text
        
        show_social = db.get_system_setting('footer_show_social')
        if show_social:
            settings['footer']['show_social'] = show_social == 'True'
    except Exception as e:
        print(f"Error getting landing page settings: {e}")
    
    return settings

'''

# Add the template functions
new_content = content[:line_end+1] + template_functions + content[line_end+1:]

# 4. Fix the context for templates
# Find the render_template calls
home_pos = new_content.find("def home():")
home_end = new_content.find("return render_template", home_pos)
home_line_end = new_content.find(")", home_end)

# Add landing page settings to home route
home_template_call = new_content[home_end:home_line_end+1]
home_template_new = home_template_call.replace(")",
                                            ", landing_page_settings=get_landing_page_settings())")

new_content = new_content[:home_end] + home_template_new + new_content[home_line_end+1:]

# Also add to login_page, dashboard, and admin_dashboard routes
for route in ['login_page', 'dashboard', 'admin_dashboard', 'projects_page', 'create_project_page', 'project_details', 'editor_page']:
    route_pos = new_content.find(f"def {route}(")
    if route_pos > 0:
        route_end = new_content.find("return render_template", route_pos)
        if route_end > 0:
            route_line_end = new_content.find(")", route_end)
            if route_line_end > 0:
                route_template_call = new_content[route_end:route_line_end+1]
                # Only add if not already there and it's a render_template call
                if "landing_page_settings" not in route_template_call and "render_template(" in route_template_call:
                    route_template_new = route_template_call.replace(")",
                                                            ", landing_page_settings=get_landing_page_settings())")
                    new_content = new_content[:route_end] + route_template_new + new_content[route_line_end+1:]
                    print(f"Added landing page settings to {route} route")

# 5. Also add to error routes
# 404
error_pos = new_content.find("def page_not_found(")
if error_pos > 0:
    error_end = new_content.find("return render_template", error_pos)
    if error_end > 0:
        error_line_end = new_content.find(")", error_end)
        if error_line_end > 0:
            error_template_call = new_content[error_end:error_line_end+1]
            if "landing_page_settings" not in error_template_call:
                error_template_new = error_template_call.replace(")",
                                                        ", landing_page_settings=get_landing_page_settings())")
                new_content = new_content[:error_end] + error_template_new + new_content[error_line_end+1:]
                print("Added landing page settings to 404 route")

# 500
error_pos = new_content.find("def server_error(")
if error_pos > 0:
    error_end = new_content.find("return render_template", error_pos)
    if error_end > 0:
        error_line_end = new_content.find(")", error_end)
        if error_line_end > 0:
            error_template_call = new_content[error_end:error_line_end+1]
            if "landing_page_settings" not in error_template_call:
                error_template_new = error_template_call.replace(")",
                                                        ", landing_page_settings=get_landing_page_settings())")
                new_content = new_content[:error_end] + error_template_new + new_content[error_line_end+1:]
                print("Added landing page settings to 500 route")

# 6. Write the updated content back to app.py
with open(app_path, 'w') as f:
    f.write(new_content)

print("\nTemplate fix completed!")
print("Run the following command to start the app in debug mode:")
print("cd /home/juanquy/OpenShot/test_app && python debug_app.py")