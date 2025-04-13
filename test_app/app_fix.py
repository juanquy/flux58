#!/usr/bin/env python3
"""
FLUX58 AI MEDIA LABS - App Fix Script
Apply fixes to the app to enable OpenShot functionality
"""

import os
import sys
import importlib
import shutil
from pathlib import Path

def create_api_module():
    """Create the API module with OpenShot status endpoint"""
    api_dir = Path("api")
    api_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    with open(api_dir / "__init__.py", "w") as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
FLUX58 AI MEDIA LABS - API Routes
API endpoints for the FLUX58 video editing web application
\"\"\"

import os
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, session

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Check if we can import OpenShot
try:
    import openshot
    from openshot_api import openshot_api
    OPENSHOT_AVAILABLE = True
except ImportError:
    OPENSHOT_AVAILABLE = False

@api_bp.route('/openshot/status')
def openshot_status():
    \"\"\"API endpoint to check OpenShot library status\"\"\"
    try:
        from openshot_api import openshot_api
        status = openshot_api.get_status()
        return jsonify(status)
    except Exception as e:
        print(f"Error getting OpenShot status: {str(e)}")
        return jsonify({
            "available": False,
            "version": "Unknown",
            "message": f"OpenShot library not available: {str(e)}",
            "capabilities": {
                "video_editing": False,
                "audio_editing": False,
                "rendering": False,
                "effects": False
            }
        })

def init_api_routes(app, db, project_manager, export_queue):
    \"\"\"Register API routes with the app\"\"\"
    app.register_blueprint(api_bp, url_prefix='/api')
""")
    
    print(f"Created API module in {api_dir}")

def add_api_routes_to_app():
    """Add code to initialize API routes in the app"""
    app_file = Path("app.py")
    if not app_file.exists():
        print(f"Error: {app_file} not found")
        return
    
    # Read app.py
    with open(app_file, "r") as f:
        content = f.read()
    
    # Check if API routes are already initialized
    if "init_api_routes(app" in content:
        print("API routes already initialized in app.py")
        return
    
    # Find appropriate location to initialize the API routes
    lines = content.split("\n")
    init_app_line = None
    for i, line in enumerate(lines):
        if "# Initialize app settings" in line:
            init_app_line = i
            break
    
    if init_app_line is None:
        print("Couldn't find appropriate location to initialize API routes")
        return
    
    # Add initialization after app.before_request line
    for i in range(init_app_line, len(lines)):
        if "app.before_request" in lines[i]:
            lines.insert(i + 2, "# Initialize API routes")
            lines.insert(i + 3, "if 'init_api_routes' in globals() and init_api_routes is not None:")
            lines.insert(i + 4, "    init_api_routes(app, db, project_manager, export_queue)")
            
            # Write back to app.py
            with open(app_file, "w") as f:
                f.write("\n".join(lines))
            
            print("Added API route initialization to app.py")
            return
    
    print("Couldn't find app.before_request line")

def create_openshot_status_endpoint():
    """Create a direct endpoint for OpenShot status if API module not used"""
    app_file = Path("app.py")
    if not app_file.exists():
        print(f"Error: {app_file} not found")
        return
    
    # Read app.py
    with open(app_file, "r") as f:
        content = f.read()
    
    # Check if the endpoint already exists
    if "@app.route('/api/openshot/status'" in content:
        print("OpenShot status endpoint already exists in app.py")
        return
    
    # Find the bottom of the API section to add our new endpoint
    lines = content.split("\n")
    
    # Add the endpoint at the end of the file
    lines.append("\n# OpenShot status endpoint for client-side checks")
    lines.append("@app.route('/api/openshot/status')")
    lines.append("def api_openshot_status():")
    lines.append("    \"\"\"API endpoint to check OpenShot library status\"\"\"")
    lines.append("    try:")
    lines.append("        if OPENSHOT_AVAILABLE:")
    lines.append("            status = {")
    lines.append("                \"available\": True,")
    lines.append("                \"version\": openshot.OPENSHOT_VERSION_FULL if hasattr(openshot, 'OPENSHOT_VERSION_FULL') else \"Unknown\",")
    lines.append("                \"message\": \"OpenShot library is available\",")
    lines.append("                \"capabilities\": {")
    lines.append("                    \"video_editing\": True,")
    lines.append("                    \"audio_editing\": True,")
    lines.append("                    \"rendering\": True,")
    lines.append("                    \"effects\": True")
    lines.append("                }")
    lines.append("            }")
    lines.append("        else:")
    lines.append("            status = {")
    lines.append("                \"available\": False,")
    lines.append("                \"version\": \"Unknown\",")
    lines.append("                \"message\": \"OpenShot library not available\",")
    lines.append("                \"capabilities\": {")
    lines.append("                    \"video_editing\": False,")
    lines.append("                    \"audio_editing\": False,")
    lines.append("                    \"rendering\": False,")
    lines.append("                    \"effects\": False")
    lines.append("                }")
    lines.append("            }")
    lines.append("        return jsonify(status)")
    lines.append("    except Exception as e:")
    lines.append("        app.logger.error(f\"Error getting OpenShot status: {str(e)}\")")
    lines.append("        return jsonify({")
    lines.append("            \"available\": False,")
    lines.append("            \"version\": \"Unknown\",")
    lines.append("            \"message\": f\"Error: {str(e)}\",")
    lines.append("            \"capabilities\": {")
    lines.append("                \"video_editing\": False,")
    lines.append("                \"audio_editing\": False,")
    lines.append("                \"rendering\": False,")
    lines.append("                \"effects\": False")
    lines.append("            }")
    lines.append("        })")
    
    # Write back to app.py
    with open(app_file, "w") as f:
        f.write("\n".join(lines))
    
    print("Added OpenShot status endpoint to app.py")

if __name__ == "__main__":
    print("Applying fixes to enable OpenShot functionality...")
    
    # Create API module
    create_api_module()
    
    # Add API routes to app
    add_api_routes_to_app()
    
    # Create OpenShot status endpoint
    create_openshot_status_endpoint()
    
    print("Fixes applied successfully!")