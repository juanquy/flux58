#!/usr/bin/env python3
import os
import re
import secrets
import shutil
from datetime import datetime

print("Starting Flask session fix script")

# 1. Create a permanent secret key file if it doesn't exist
secret_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.flask_secret_key')

if not os.path.exists(secret_key_file):
    # Generate a new secret key
    secret_key = secrets.token_hex(32)  # 64 character hex string
    
    # Save to file
    with open(secret_key_file, 'w') as f:
        f.write(secret_key)
    print(f"Created new permanent secret key file: {secret_key_file}")
else:
    with open(secret_key_file, 'r') as f:
        secret_key = f.read().strip()
    print(f"Using existing secret key from file: {secret_key_file}")

# 2. Backup app.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

# 3. Update app.py to load the secret key from file
with open(app_path, 'r') as f:
    app_code = f.read()

# Check if secrets is imported
if 'import secrets' not in app_code:
    app_code = app_code.replace('import uuid', 'import uuid\nimport secrets')
    print("Added missing import for secrets module")

# Check for existing secret key setting
pattern = r"app\.config\['SECRET_KEY'\] = .*"
secret_key_code = f"# Load secret key from file\ntry:\n    with open('.flask_secret_key', 'r') as f:\n        app.config['SECRET_KEY'] = f.read().strip()\nexcept Exception as e:\n    app.config['SECRET_KEY'] = secrets.token_hex(32)\n    print(f\"Warning: Using temporary secret key. Fix the secret key file.\")"

if re.search(pattern, app_code):
    # Replace existing secret key setting
    app_code = re.sub(pattern, secret_key_code, app_code)
    print("Replaced existing secret key setting")
else:
    # Add new secret key setting after Flask app initialization
    app_code = app_code.replace('app = Flask(__name__)', 'app = Flask(__name__)\n' + secret_key_code)
    print("Added new secret key setting")

# Add permanent session setting
if 'session.permanent = True' not in app_code:
    # Find a good place to add it - after request handlers but before routes
    if '@app.before_request' in app_code:
        # Add after the last @app.before_request function
        sections = app_code.split('@app.before_request')
        last_section = sections[-1]
        end_of_func = last_section.find('\n\n')
        if end_of_func > 0:
            sections[-1] = last_section[:end_of_func+2] + "\n# Make sessions permanent by default\n@app.before_request\ndef make_session_permanent():\n    session.permanent = True\n" + last_section[end_of_func+2:]
            app_code = '@app.before_request'.join(sections)
            print("Added session permanence setting after existing before_request handlers")
    else:
        # No existing before_request, add after app initialization
        app_code = app_code.replace(secret_key_code, secret_key_code + "\n\n# Make sessions permanent by default\n@app.before_request\ndef make_session_permanent():\n    session.permanent = True")
        print("Added session permanence setting as new before_request handler")

# Set session lifetime to 7 days
if "app.config['PERMANENT_SESSION_LIFETIME']" not in app_code:
    # Add after secret key setting
    app_code = app_code.replace(secret_key_code, secret_key_code + "\n# Set permanent session lifetime to 7 days\nfrom datetime import timedelta\napp.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)")
    print("Added session lifetime setting")

# Check if Flask-Session is imported and configured
if 'from flask_session import Session' not in app_code:
    # Add import
    app_code = app_code.replace('from flask import ', 'from flask import ')
    
    # Don't add Flask-Session for now, as it requires additional setup

# Write updated code back to app.py
with open(app_path, 'w') as f:
    f.write(app_code)
print("Updated app.py with session fixes")

# 4. Update service file to use fixed version
service_path = '/home/juanquy/OpenShot/test_app/openshot-web-fixed.service'
with open(service_path, 'r') as f:
    service_content = f.read()

if 'DB_TYPE=postgres' not in service_content:
    print("Service file is missing important environment variables!")
    print("Please run the following commands to update the service:")
    print("sudo systemctl stop openshot-web.service")
    print("sudo cp /home/juanquy/OpenShot/test_app/openshot-web-fixed.service /etc/systemd/system/openshot-web.service")
    print("sudo systemctl daemon-reload")
else:
    print("Service file already includes required environment variables")

print("\nFlask session fixes completed successfully!")
print("Run the following commands to restart the service:")
print("sudo systemctl stop openshot-web.service")
print("sudo systemctl start openshot-web.service")
print("sudo systemctl status openshot-web.service")