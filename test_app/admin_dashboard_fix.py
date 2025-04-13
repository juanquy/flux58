#!/usr/bin/env python3
"""
FLUX58 Admin Dashboard Fix - March 21, 2025
This script fixes string formatting errors in the admin dashboard that were causing
500 Internal Server Errors when admin users log in.
"""
import os
import sys
import time
import traceback
from datetime import datetime
import json

# Print banner
print("-" * 80)
print("FLUX58 Admin Dashboard Fix - March 21, 2025")
print("This script fixes string formatting in the admin dashboard")
print("-" * 80)

# Try to locate the app.py file
if not os.path.exists('app.py'):
    print("Error: app.py not found in current directory")
    sys.exit(1)

# Make a backup of the original file
timestamp = int(time.time())
backup_filename = f"app.py.admin_dashboard_fix_{timestamp}"
print(f"Creating backup: {backup_filename}")
os.system(f"cp app.py {backup_filename}")

# Apply fixes
print("Applying fixes...")

# Fix 1: Fix string formatting in admin dashboard recent activity
def fix_admin_dashboard_formatting():
    print("1. Fixing string formatting in admin dashboard...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix project creation activity formatting
    content = content.replace(
        'recent_activity.append({\n'
        '            "icon": "bi-film",\n'
        '            "description": "{username} created project: {}".format(project[\'name\']),\n'
        '            "time": format_timestamp(project[\'created_at\'])\n'
        '        })',
        
        'recent_activity.append({\n'
        '            "icon": "bi-film",\n'
        '            "description": "{} created project: {}".format(username, project[\'name\']),\n'
        '            "time": format_timestamp(project[\'created_at\'])\n'
        '        })'
    )
    
    # Fix export activity formatting
    content = content.replace(
        'recent_activity.append({\n'
        '            "icon": "bi-cloud-arrow-up",\n'
        '            "description": "{username} exported project (format: {})".format(export[\'format\']),\n'
        '            "time": format_timestamp(export[\'started_at\'])\n'
        '        })',
        
        'recent_activity.append({\n'
        '            "icon": "bi-cloud-arrow-up",\n'
        '            "description": "{} exported project (format: {})".format(username, export[\'format\']),\n'
        '            "time": format_timestamp(export[\'started_at\'])\n'
        '        })'
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    return True

# Apply the fix
fixes_applied = 0
try:
    if fix_admin_dashboard_formatting():
        fixes_applied += 1
except Exception as e:
    print(f"Error applying fix_admin_dashboard_formatting: {str(e)}")
    traceback.print_exc()

# Summary
print("-" * 80)
print(f"Applied {fixes_applied}/1 fixes successfully")
print(f"Original file backed up as: {backup_filename}")
print("Please restart the Flask application to apply changes")
print("-" * 80)

print("\nFix application complete!")

# Execute the script if run directly
if __name__ == "__main__":
    # Script already executed above
    pass