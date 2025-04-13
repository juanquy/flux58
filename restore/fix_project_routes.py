#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

print("Starting Project Routes Fix Script")

# 1. Backup app.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

# 2. Add the project creation routes to app.py
with open(app_path, 'r') as f:
    app_code = f.read()

# Look for a good place to add the routes - after other project routes
projects_section_marker = "@app.route('/projects')"

projects_routes = """

@app.route('/projects/new', methods=['GET', 'POST'])
def create_project_page():
    \"\"\"Create a new project\"\"\"
    if 'user_id' not in session:
        flash('Please log in to create a project', 'warning')
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Project name is required', 'danger')
            return render_template('create_project.html')
        
        user_id = session['user_id']
        
        # Set up project settings from form
        resolution = request.form.get('resolution', '1080p')
        framerate = request.form.get('framerate', '30')
        audio_channels = int(request.form.get('audioChannels', 2))
        
        # Handle custom resolution
        width, height = 1920, 1080  # Default to 1080p
        if resolution == '720p':
            width, height = 1280, 720
        elif resolution == '4k':
            width, height = 3840, 2160
        elif resolution == 'custom':
            width = int(request.form.get('customWidth', 1920))
            height = int(request.form.get('customHeight', 1080))
            
        # Handle custom framerate
        fps = 30  # Default
        if framerate == '24':
            fps = 24
        elif framerate == '60':
            fps = 60
        elif framerate == 'custom':
            fps = float(request.form.get('customFPS', 30))
        
        # Log the project creation attempt
        print(f"Creating project: {name}, {description}, User ID: {user_id}")
        
        # Create the project
        project = project_manager.create_project(user_id, name, description)
        
        if project:
            # Project created successfully
            flash('Project created successfully!', 'success')
            return redirect(url_for('editor_page', project_id=project['id']))
        else:
            # Project creation failed
            flash('Failed to create project. Please try again.', 'danger')
            return render_template('create_project.html')
    
    # GET request
    return render_template('create_project.html')

@app.route('/projects/<project_id>')
def project_details(project_id):
    \"\"\"View project details\"\"\"
    if 'user_id' not in session:
        flash('Please log in to view project details', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    project = project_manager.get_project(project_id)
    
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('projects_page'))
    
    if project['user_id'] != user_id and session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('projects_page'))
    
    return render_template('project_details.html', project=project)
"""

projects_page_route = """
@app.route('/projects')
def projects_page():
    \"\"\"List all user projects\"\"\"
    if 'user_id' not in session:
        flash('Please log in to view your projects', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    projects = project_manager.list_user_projects(user_id)
    
    return render_template('projects.html', projects=projects)
"""

editor_route = """

@app.route('/editor')
def editor_page():
    \"\"\"Video editor page\"\"\"
    if 'user_id' not in session:
        flash('Please log in to access the editor', 'warning')
        return redirect(url_for('login_page'))
    
    project_id = request.args.get('project_id')
    if not project_id:
        flash('Project ID is required', 'danger')
        return redirect(url_for('projects_page'))
    
    user_id = session['user_id']
    project = project_manager.get_project(project_id)
    
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('projects_page'))
    
    if project['user_id'] != user_id and session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('projects_page'))
    
    return render_template('editor.html', project=project)
"""

# Check if we need to add the projects page route
if projects_section_marker not in app_code:
    print("Adding projects page route")
    
    # Find a good place to add it - after another route
    routes = app_code.split("@app.route")
    if len(routes) > 2:  # First will be empty string
        # Insert after the second route
        insert_index = app_code.find("@app.route", app_code.find("@app.route") + 1)
        # Find the next blank line after this route
        next_blank_line = app_code.find("\n\n", insert_index)
        if next_blank_line > 0:
            new_app_code = app_code[:next_blank_line] + projects_page_route + app_code[next_blank_line:]
            app_code = new_app_code
            print("Added projects page route")
        else:
            print("Could not find where to add projects page route")
    else:
        print("Could not find where to add projects page route")

# Check if we need to add the project creation routes
if "@app.route('/projects/new'" not in app_code:
    print("Adding project creation routes")
    
    # Find projects_page route if it exists now
    if projects_section_marker in app_code:
        # Find the end of the function
        projects_section_index = app_code.find(projects_section_marker)
        next_blank_line = app_code.find("\n\n", projects_section_index)
        if next_blank_line > 0:
            new_app_code = app_code[:next_blank_line] + projects_routes + app_code[next_blank_line:]
            app_code = new_app_code
            print("Added project creation routes")
        else:
            # Append to end of file
            app_code += projects_routes
            print("Added project creation routes to end of file")
    else:
        # Append to end of file
        app_code += projects_routes
        print("Added project creation routes to end of file")

# Check if we need to add the editor route
if "@app.route('/editor'" not in app_code:
    print("Adding editor route")
    # Append to end of file
    app_code += editor_route
    print("Added editor route to end of file")

# Write the updated code back to the file
with open(app_path, 'w') as f:
    f.write(app_code)

print("\nProject routes fix completed!")
print("Run the following commands to restart the service:")
print("sudo systemctl stop openshot-web.service")
print("sudo systemctl start openshot-web.service")
print("sudo systemctl status openshot-web.service")