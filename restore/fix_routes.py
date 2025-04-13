#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

print("Starting Route Fix Script")

# 1. Backup app.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

# 2. Read the current app.py file
with open(app_path, 'r') as f:
    content = f.read()

# 3. Define the new routes to add
new_routes = '''
# Project management routes
@app.route('/projects')
def projects_page():
    """List all user projects"""
    if 'user_id' not in session:
        flash('Please log in to view your projects', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    projects = project_manager.list_user_projects(user_id)
    
    return render_template('projects.html', projects=projects)

@app.route('/projects/new', methods=['GET', 'POST'])
def create_project_page():
    """Create a new project"""
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
        
        try:
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
        except Exception as e:
            print(f"Error creating project: {str(e)}")
            flash('An error occurred while creating the project', 'danger')
            return render_template('create_project.html')
    
    # GET request
    return render_template('create_project.html')

@app.route('/projects/<project_id>')
def project_details(project_id):
    """View project details"""
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
    """Delete a project"""
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

@app.route('/editor')
def editor_page():
    """Video editor page"""
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
'''

# 4. Find a good place to add the routes
# Look for a route definition to insert after
route_positions = []
for i in range(len(content) - 15):
    if content[i:i+11] == "@app.route(":
        route_positions.append(i)

if route_positions:
    # Get last route position
    last_route_pos = route_positions[-1]
    
    # Find the end of the function (next blank lines)
    end_of_last_function = content.find("\n\n", last_route_pos + 100)
    if end_of_last_function == -1:
        end_of_last_function = len(content)
    
    # Add the new routes
    new_content = content[:end_of_last_function] + new_routes + content[end_of_last_function:]
    
    # Write the updated content back to app.py
    with open(app_path, 'w') as f:
        f.write(new_content)
    
    print("Added project routes to app.py")
else:
    print("Could not find a suitable place to add routes")

print("\nRoute fix completed!")
print("Run the following command to start the app in debug mode:")
print("cd /home/juanquy/OpenShot/test_app && python debug_app.py")