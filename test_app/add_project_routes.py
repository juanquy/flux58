#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

print("Starting Project Routes Update Script")

# 1. Backup app.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

# 2. Find project routes in app.py
with open(app_path, 'r') as f:
    app_code = f.read()

# Check if project deletion route exists
if "@app.route('/projects/<project_id>/delete'" not in app_code:
    # Find where to add the route - after other project routes
    if "@app.route('/projects/<project_id>')" in app_code:
        # Find the end of the project_details function
        project_details_pos = app_code.find("@app.route('/projects/<project_id>')")
        
        # Find the end of the function (next route or end of file)
        next_route_pos = len(app_code)
        for pos in range(project_details_pos + 100, len(app_code) - 15):
            if app_code[pos:pos+11] == "@app.route(":
                next_route_pos = pos
                break
                
        # Project delete route to add
        delete_route = """

@app.route('/projects/<project_id>/delete', methods=['POST'])
def delete_project(project_id):
    \"\"\"Delete a project\"\"\"
    if 'user_id' not in session:
        flash('Please log in to delete projects', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    project = project_manager.get_project(project_id)
    
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('projects_page'))
    
    # Check if user owns the project or is admin
    if project['user_id'] != user_id and session.get('role') != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('projects_page'))
    
    # Delete the project
    success = project_manager.delete_project(project_id)
    
    if success:
        flash('Project deleted successfully', 'success')
    else:
        flash('Failed to delete project', 'danger')
    
    return redirect(url_for('projects_page'))
"""
        # Add the delete route
        new_app_code = app_code[:next_route_pos] + delete_route + app_code[next_route_pos:]
        app_code = new_app_code
        print("Added project delete route")
    else:
        print("Could not find where to add delete route - project_details route not found")

# Fix the project details route if it's causing Internal Server Error
if "@app.route('/projects/<project_id>')" in app_code:
    # Get the route function and check for issues
    project_details_pos = app_code.find("@app.route('/projects/<project_id>')")
    project_details_func_start = app_code.find("def project_details", project_details_pos)
    
    # Find the end of the function (next route or end of file)
    next_route_pos = len(app_code)
    for pos in range(project_details_pos + 100, len(app_code) - 15):
        if app_code[pos:pos+11] == "@app.route(":
            next_route_pos = pos
            break
    
    # Extract current function
    project_details_func = app_code[project_details_pos:next_route_pos]
    
    # Check if there are issues with the function
    if 'NoneType' in project_details_func or 'Internal Server Error' in project_details_func:
        # Replace with fixed version
        fixed_project_details = """
@app.route('/projects/<project_id>')
def project_details(project_id):
    \"\"\"View project details\"\"\"
    if 'user_id' not in session:
        flash('Please log in to view project details', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    
    try:
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found', 'danger')
            return redirect(url_for('projects_page'))
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('projects_page'))
        
        # Get user credits
        user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
        available_credits = user_credits["total"] - user_credits["used"]
        
        return render_template(
            'project_details.html', 
            project=project,
            credits=available_credits
        )
    except Exception as e:
        print(f"Error getting project details: {str(e)}")
        flash('An error occurred while loading project details', 'danger')
        return redirect(url_for('projects_page'))
"""
        # Replace the function
        new_app_code = app_code[:project_details_pos] + fixed_project_details + app_code[next_route_pos:]
        app_code = new_app_code
        print("Fixed project_details route")
    else:
        print("project_details route looks OK")

# Fix the editor page route if it's causing Internal Server Error
if "@app.route('/editor')" in app_code:
    # Get the route function and check for issues
    editor_pos = app_code.find("@app.route('/editor')")
    editor_func_start = app_code.find("def editor_page", editor_pos)
    
    # Find the end of the function (next route or end of file)
    next_route_pos = len(app_code)
    for pos in range(editor_pos + 100, len(app_code) - 15):
        if app_code[pos:pos+11] == "@app.route(":
            next_route_pos = pos
            break
    
    # Extract current function
    editor_func = app_code[editor_pos:next_route_pos]
    
    # Check if there are issues with the function
    if 'NoneType' in editor_func or 'Internal Server Error' in editor_func:
        # Replace with fixed version
        fixed_editor = """
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
    
    try:
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found', 'danger')
            return redirect(url_for('projects_page'))
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('projects_page'))
        
        # Get user credits
        user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
        available_credits = user_credits["total"] - user_credits["used"]
        
        return render_template(
            'editor.html', 
            project=project,
            credits=available_credits
        )
    except Exception as e:
        print(f"Error loading editor: {str(e)}")
        flash('An error occurred while loading the editor', 'danger')
        return redirect(url_for('projects_page'))
"""
        # Replace the function
        new_app_code = app_code[:editor_pos] + fixed_editor + app_code[next_route_pos:]
        app_code = new_app_code
        print("Fixed editor_page route")
    else:
        print("editor_page route looks OK")
        
# Add routes if they don't exist
if "@app.route('/projects/<project_id>')" not in app_code:
    # Find where to add the route
    if "@app.route('/projects')" in app_code:
        # Find the end of the projects_page function
        projects_pos = app_code.find("@app.route('/projects')")
        
        # Find the end of the function (next route or end of file)
        next_route_pos = len(app_code)
        for pos in range(projects_pos + 100, len(app_code) - 15):
            if app_code[pos:pos+11] == "@app.route(":
                next_route_pos = pos
                break
        
        # New routes to add
        new_routes = """

@app.route('/projects/<project_id>')
def project_details(project_id):
    \"\"\"View project details\"\"\"
    if 'user_id' not in session:
        flash('Please log in to view project details', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    
    try:
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found', 'danger')
            return redirect(url_for('projects_page'))
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('projects_page'))
        
        # Get user credits
        user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
        available_credits = user_credits["total"] - user_credits["used"]
        
        return render_template(
            'project_details.html', 
            project=project,
            credits=available_credits
        )
    except Exception as e:
        print(f"Error getting project details: {str(e)}")
        flash('An error occurred while loading project details', 'danger')
        return redirect(url_for('projects_page'))

@app.route('/projects/<project_id>/delete', methods=['POST'])
def delete_project(project_id):
    \"\"\"Delete a project\"\"\"
    if 'user_id' not in session:
        flash('Please log in to delete projects', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    
    try:
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found', 'danger')
            return redirect(url_for('projects_page'))
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('projects_page'))
        
        # Delete the project
        success = project_manager.delete_project(project_id)
        
        if success:
            flash('Project deleted successfully', 'success')
        else:
            flash('Failed to delete project', 'danger')
        
        return redirect(url_for('projects_page'))
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
        flash('An error occurred while deleting the project', 'danger')
        return redirect(url_for('projects_page'))
"""
        # Add the new routes
        new_app_code = app_code[:next_route_pos] + new_routes + app_code[next_route_pos:]
        app_code = new_app_code
        print("Added project_details and delete_project routes")
    else:
        print("Could not find where to add routes - projects_page route not found")

if "@app.route('/editor')" not in app_code:
    # Find a good place to add the route
    route_positions = []
    for i in range(len(app_code) - 15):
        if app_code[i:i+11] == "@app.route(":
            route_positions.append(i)
    
    if route_positions:
        # Get last route position
        last_route_pos = route_positions[-1]
        
        # Find the end of the function (next blank lines)
        end_of_last_function = app_code.find("\n\n", last_route_pos + 100)
        if end_of_last_function == -1:
            end_of_last_function = len(app_code)
        
        # Editor route to add
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
    
    try:
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found', 'danger')
            return redirect(url_for('projects_page'))
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('projects_page'))
        
        # Get user credits
        user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
        available_credits = user_credits["total"] - user_credits["used"]
        
        return render_template(
            'editor.html', 
            project=project,
            credits=available_credits
        )
    except Exception as e:
        print(f"Error loading editor: {str(e)}")
        flash('An error occurred while loading the editor', 'danger')
        return redirect(url_for('projects_page'))
"""
        # Add the editor route
        new_app_code = app_code[:end_of_last_function] + editor_route + app_code[end_of_last_function:]
        app_code = new_app_code
        print("Added editor_page route")
    else:
        print("Could not find a place to add editor_page route")

# Write the updated code back to the file
with open(app_path, 'w') as f:
    f.write(app_code)
    print("Saved changes to app.py")

print("\nProject routes update completed!")
print("Run the following commands to restart the service:")
print("sudo systemctl restart openshot-web.service")