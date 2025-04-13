#!/usr/bin/env python3
"""
Inject media routes into the main app.py file
"""
import os
import shutil
import re
from datetime import datetime

# Create a backup of app.py
APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
BACKUP_PATH = f"{APP_PATH}.media_routes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

print(f"Creating backup of app.py at {BACKUP_PATH}")
shutil.copy2(APP_PATH, BACKUP_PATH)

# Read the app.py file
with open(APP_PATH, 'r') as f:
    app_code = f.read()

# Check if media_server import already exists
if "from media_server import add_media_routes" not in app_code:
    # Find the best place to add the import
    import_section_end = app_code.find("# Initialize Flask app")
    if import_section_end == -1:
        import_section_end = app_code.find("app = Flask")
    
    if import_section_end != -1:
        # Add the import
        import_code = "from media_server import add_media_routes\n"
        new_app_code = app_code[:import_section_end] + import_code + app_code[import_section_end:]
        
        # Find the initialization section to add the media routes
        init_section = new_app_code.find("# Initialize the app")
        if init_section == -1:
            init_section = new_app_code.find("if __name__ == '__main__':")
        
        if init_section != -1:
            # Find a good spot before the main block
            init_code = "\n# Add media serving routes\nadd_media_routes(app)\n"
            
            # Insert before the main block
            new_app_code = new_app_code[:init_section] + init_code + new_app_code[init_section:]
            
            # Write the updated code back to app.py
            with open(APP_PATH, 'w') as f:
                f.write(new_app_code)
            
            print("Media server routes added to app.py")
        else:
            print("Could not find initialization section in app.py")
    else:
        print("Could not find import section in app.py")
else:
    print("Media server routes already imported in app.py")

# Update the config section to ensure UPLOAD_FOLDER is defined
if "UPLOAD_FOLDER" not in app_code:
    # Find the config section
    config_section = app_code.find("app.config[")
    if config_section != -1:
        # Look for the end of the config section
        config_end = app_code.find("# Initialize", config_section)
        if config_end == -1:
            config_end = app_code.find("@app.route", config_section)
        
        if config_end != -1:
            # Add the UPLOAD_FOLDER config
            config_code = "\n# Upload folder for media files\napp.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'uploads')\n"
            config_code += "app.config['ALLOWED_EXTENSIONS'] = {\n"
            config_code += "    'video': ['mp4', 'webm', 'mov', 'avi'],\n"
            config_code += "    'audio': ['mp3', 'wav', 'ogg', 'aac'],\n"
            config_code += "    'image': ['jpg', 'jpeg', 'png', 'gif', 'webp']\n"
            config_code += "}\n"
            
            # Insert before the end of the config section
            new_app_code = app_code[:config_end] + config_code + app_code[config_end:]
            
            # Write the updated code back to app.py
            with open(APP_PATH, 'w') as f:
                f.write(new_app_code)
            
            print("UPLOAD_FOLDER config added to app.py")
        else:
            print("Could not find the end of config section in app.py")
    else:
        print("Could not find config section in app.py")
else:
    print("UPLOAD_FOLDER already defined in app.py")

print("\nMedia route injection complete!")
print("Restart the application for changes to take effect.")