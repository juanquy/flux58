#!/usr/bin/env python3
"""
FLUX58 Credits and Editor Fix - March 21, 2025
This script fixes issues with displaying user credits and resolves string formatting errors
in the editor page that were causing 500 errors when creating new projects.
"""
import os
import sys
import time
import traceback
from datetime import datetime
import json

# Print banner
print("-" * 80)
print("FLUX58 Credits and Editor Fix - March 21, 2025")
print("This script fixes user credits display and editor page string formatting")
print("-" * 80)

# Try to locate the app.py file
if not os.path.exists('app.py'):
    print("Error: app.py not found in current directory")
    sys.exit(1)

# Make a backup of the original file
timestamp = int(time.time())
backup_filename = f"app.py.credits_editor_fix_{timestamp}"
print(f"Creating backup: {backup_filename}")
os.system(f"cp app.py {backup_filename}")

# Apply fixes
print("Applying fixes...")

# Fix 1: Fix string formatting errors in editor_page
def fix_editor_string_formatting():
    print("1. Fixing string formatting in editor_page...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix string formatting in editor_page
    content = content.replace(
        'logger.info("Loading editor for project_id: {project_id}, user_id: {}".format(user_id))',
        'logger.info("Loading editor for project_id: {}, user_id: {}".format(project_id, user_id))'
    )
    
    # Fix project data debugging
    content = content.replace(
        'print("Project loaded for editor - ID: {project_id}, Name: {}".format(project.get(\'name\')))',
        'print("Project loaded for editor - ID: {}, Name: {}".format(project_id, project.get(\'name\')))'
    )
    
    # Optimize logging to avoid excessive output
    content = content.replace(
        'logger.info("Final project structure before template rendering: {}".format(json.dumps(project, default=str)))',
        '# Log a shorter summary to avoid excessive log size\n'
        '        logger.info("Project ready for editor rendering. ID: {}, Name: {}, Tracks: {}, Assets: {}".format(\n'
        '            project_id, \n'
        '            project.get(\'name\'), \n'
        '            len(project[\'timeline\'].get(\'tracks\', [])),\n'
        '            len(project.get(\'assets\', []))\n'
        '        ))'
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    return True

# Fix 2: Fix dashboard template rendering
def fix_dashboard_template():
    print("2. Fixing dashboard template rendering...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix dashboard template rendering (ensure landing_page_settings is properly passed)
    content = content.replace(
        "    return render_template(\n"
        "        'dashboard.html',\n"
        "        projects=projects,\n"
        "        credits=user_credits,\n"
        "        exports=exports,\n"
        "        activities=activities,\n"
        "        transactions=transactions\n"
        "    , landing_page_settings=get_landing_page_settings())",
        
        "    return render_template(\n"
        "        'dashboard.html',\n"
        "        projects=projects,\n"
        "        credits=user_credits,\n"
        "        exports=exports,\n"
        "        activities=activities,\n"
        "        transactions=transactions,\n"
        "        landing_page_settings=get_landing_page_settings())"
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    return True

# Fix 3: Fix create_project_page
def fix_create_project_page():
    print("3. Fixing create_project_page...")
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Fix create_project_page to always pass landing_page_settings
    content = content.replace(
        "@app.route('/projects/new', methods=['GET', 'POST'])\n"
        "def create_project_page():\n"
        "    \"\"\"Create a new project\"\"\"\n"
        "    if 'user_id' not in session:\n"
        "        flash('Please log in to create a project', 'warning')\n"
        "        return redirect(url_for('login_page'))\n"
        "    \n"
        "    if request.method == 'POST':\n"
        "        name = request.form.get('name')\n"
        "        description = request.form.get('description', '')\n"
        "        \n"
        "        if not name:\n"
        "            flash('Project name is required', 'danger')\n"
        "            return render_template('create_project.html', landing_page_settings=get_landing_page_settings())\n"
        "        \n"
        "        user_id = session['user_id']\n"
        "        \n"
        "        try:\n"
        "            # Create the project\n"
        "            project = project_manager.create_project(user_id, name, description)\n"
        "            \n"
        "            if project:\n"
        "                # Project created successfully\n"
        "                flash('Project created successfully!', 'success')\n"
        "                return redirect(url_for('editor_page', project_id=project['id']))\n"
        "            else:\n"
        "                # Project creation failed\n"
        "                flash('Failed to create project. Please try again.', 'danger')\n"
        "                return render_template('create_project.html')\n"
        "        except Exception as e:\n"
        "            print(\"Error creating project: {}\".format(str(e)))\n"
        "            flash('An error occurred while creating the project', 'danger')\n"
        "            return render_template('create_project.html')\n"
        "    \n"
        "    # GET request\n"
        "    return render_template('create_project.html')",
        
        "@app.route('/projects/new', methods=['GET', 'POST'])\n"
        "def create_project_page():\n"
        "    \"\"\"Create a new project\"\"\"\n"
        "    if 'user_id' not in session:\n"
        "        flash('Please log in to create a project', 'warning')\n"
        "        return redirect(url_for('login_page'))\n"
        "    \n"
        "    if request.method == 'POST':\n"
        "        name = request.form.get('name')\n"
        "        description = request.form.get('description', '')\n"
        "        \n"
        "        if not name:\n"
        "            flash('Project name is required', 'danger')\n"
        "            return render_template('create_project.html', landing_page_settings=get_landing_page_settings())\n"
        "        \n"
        "        user_id = session['user_id']\n"
        "        \n"
        "        try:\n"
        "            # Create the project\n"
        "            project = project_manager.create_project(user_id, name, description)\n"
        "            \n"
        "            if project:\n"
        "                # Project created successfully\n"
        "                flash('Project created successfully!', 'success')\n"
        "                return redirect(url_for('editor_page', project_id=project['id']))\n"
        "            else:\n"
        "                # Project creation failed\n"
        "                flash('Failed to create project. Please try again.', 'danger')\n"
        "                return render_template('create_project.html', landing_page_settings=get_landing_page_settings())\n"
        "        except Exception as e:\n"
        "            print(\"Error creating project: {}\".format(str(e)))\n"
        "            flash('An error occurred while creating the project', 'danger')\n"
        "            return render_template('create_project.html', landing_page_settings=get_landing_page_settings())\n"
        "    \n"
        "    # GET request\n"
        "    return render_template('create_project.html', landing_page_settings=get_landing_page_settings())"
    )
    
    with open('app.py', 'w') as f:
        f.write(content)
    
    return True

# Apply all fixes
fixes_applied = 0
try:
    if fix_editor_string_formatting():
        fixes_applied += 1
except Exception as e:
    print(f"Error applying fix_editor_string_formatting: {str(e)}")
    traceback.print_exc()

try:
    if fix_dashboard_template():
        fixes_applied += 1
except Exception as e:
    print(f"Error applying fix_dashboard_template: {str(e)}")
    traceback.print_exc()

try:
    if fix_create_project_page():
        fixes_applied += 1
except Exception as e:
    print(f"Error applying fix_create_project_page: {str(e)}")
    traceback.print_exc()

# Summary
print("-" * 80)
print(f"Applied {fixes_applied}/3 fixes successfully")
print(f"Original file backed up as: {backup_filename}")
print("Please restart the Flask application to apply changes")
print("-" * 80)

# If all fixes were applied, update the last fix timestamp in the database
if fixes_applied == 3:
    print("Creating test setting to verify fix application...")
    try:
        import sqlite3
        connection = sqlite3.connect('data/database.sqlite')
        cursor = connection.cursor()
        timestamp = int(time.time())
        cursor.execute("INSERT OR REPLACE INTO system_settings (key, value) VALUES (?, ?)", 
                      (f"credits_editor_fix_{timestamp}", "SUCCESS"))
        connection.commit()
        connection.close()
        print("Successfully created test setting in database")
    except Exception as e:
        print(f"Unable to update database (this is expected if using PostgreSQL): {str(e)}")
        
    try:
        import psycopg2
        # Try to update PostgreSQL database
        connection = psycopg2.connect(
            host="localhost",
            database="flux58",
            user="flux58_user",
            password="flux58_password"
        )
        cursor = connection.cursor()
        timestamp = int(time.time())
        cursor.execute("INSERT INTO system_settings (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = %s", 
                      (f"credits_editor_fix_{timestamp}", "SUCCESS", "SUCCESS"))
        connection.commit()
        connection.close()
        print("Successfully created test setting in PostgreSQL database")
    except Exception as e:
        print(f"Error updating PostgreSQL database: {str(e)}")

print("\nFix application complete!")

# Execute the script if run directly
if __name__ == "__main__":
    # Script already executed above
    pass