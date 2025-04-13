import os
import shutil

print("Creating fresh project routes from scratch")

# 1. Backup app.py
app_path = '/home/juanquy/OpenShot/test_app/app.py'
backup_path = app_path + '.original'
shutil.copy2(app_path, backup_path)
print(f"Created backup at {backup_path}")

# 2. Create a simple app with only the project routes we need
# This is a simplified version that includes only what we need
simple_app = '''from flask import Flask, jsonify, request, redirect, url_for, render_template, session, send_file, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import uuid
import json
import shutil
import time
from datetime import datetime, timedelta
import secrets

# Import python-dotenv for loading environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file if it exists
    load_dotenv()
except ImportError:
    # python-dotenv is not installed, log a warning
    print("Warning: python-dotenv is not installed. Environment variables will not be loaded from .env file.")

# Import our custom modules
import logging
from database import Database
from projects import ProjectManager
from openshot_api import OpenShotVideoAPI
import logger
import export_queue
from admin_tools import AdminTools
from paypal_integration import PayPalAPI
from flask import request, g

# Initialize Flask app
app = Flask(__name__)
# Load secret key from file
try:
    with open('.flask_secret_key', 'r') as f:
        app.config['SECRET_KEY'] = f.read().strip()
except Exception as e:
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    print(f"Warning: Using temporary secret key. Fix the secret key file.")
# Set permanent session lifetime to 7 days
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload
app.config['UPLOAD_FOLDER'] = os.path.join('data', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {
    'video': {'mp4', 'mov', 'avi', 'mkv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'aac'},
    'image': {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'}
}
app.config['LOG_LEVEL'] = logging.INFO
app.config['EXPORT_CONCURRENT_JOBS'] = 2  # Number of concurrent export jobs

# Database configuration
DB_TYPE = 'postgres'  # Use PostgreSQL
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

# Initialize our database and managers
db = Database(use_postgres=True, host=DB_HOST, port=DB_PORT, 
              database=DB_NAME, user=DB_USER, password=DB_PASS)
print(f"Using PostgreSQL database: {DB_NAME} on {DB_HOST}:{DB_PORT}")

# Make database available to projects module before creating ProjectManager
import projects
projects.db = db
project_manager = ProjectManager(base_path='data')
openshot_api = OpenShotVideoAPI(data_path='data')

# Initialize logging system
log = logger.init_logger(database=db, log_dir='logs', log_level=app.config['LOG_LEVEL'])
logger.info("Application starting", "app")

# Initialize admin tools
admin_tools = AdminTools(database=db, backup_dir='backups')

# Create admin account if it doesn't exist
admin = db.get_user_by_username('admin')
if not admin:
    logger.info("Creating admin account", "app")
    admin_id = str(uuid.uuid4())
    db.create_user(
        user_id=admin_id,
        username="admin",
        password_hash=generate_password_hash("admin123"),
        email="admin@flux58.com",
        role="admin"
    )
    
    # Initialize admin credits
    db.add_credits(
        user_id=admin_id,
        amount=9999,
        transaction_type="initial",
        description="Admin account setup"
    )
    
    logger.info("Admin account created successfully", "app")

# Initialize PayPal API
paypal_api = PayPalAPI()
    
# Clean up expired sessions
db.cleanup_expired_sessions()

# Make sessions permanent by default
@app.before_request
def make_session_permanent():
    session.permanent = True

# Decorator for admin-only routes
def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"ADMIN_REQUIRED DECORATOR - Session: {session}")
        
        if 'user_id' not in session:
            print("No user_id in session - redirecting to login")
            flash('Please log in to access the admin panel', 'warning')
            return redirect(url_for('login_page'))
        
        user_id = session['user_id']
        username = session.get('username')
        role = session.get('role')
        
        print(f"Admin check - User ID: {user_id}, Username: {username}, Role from session: {role}")
        
        # Get user from database
        user = db.get_user_by_username(username)
        print(f"User from database: {user}")
        
        if not user:
            print("User not found in database")
            flash('Admin privileges required', 'danger')
            return redirect(url_for('dashboard'))
            
        db_role = user.get('role')
        print(f"Role from database: {db_role}")
        
        if db_role != 'admin':
            print(f"User doesn't have admin role (role={db_role})")
            flash('Admin privileges required', 'danger')
            return redirect(url_for('dashboard'))
            
        print("Admin check passed - user is an admin")
        return f(*args, **kwargs)
    return decorated_function

# Helper function for formatting timestamps
def format_timestamp(timestamp):
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    else:
        dt = timestamp
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return dt.strftime("%b %d, %Y")

# Home page
@app.route('/')
def home():
    """Home page"""
    # Check if user is logged in
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    
    # Home page settings
    title = db.get_system_setting('landing_page_title', 'FLUX58 AI MEDIA LABS')
    subtitle = db.get_system_setting('landing_page_subtitle', 'Powerful AI-Enhanced Video Editing')
    description = db.get_system_setting('landing_page_description', 
                               'Create professional videos with our cloud-based video editor, powered by AI')
    
    hero_image = db.get_system_setting('landing_page_hero_image', '/static/img/custom/openshot-banner.jpg')
    
    # Try to initialize landing page settings if they don't exist
    try:
        if not title or not subtitle or not description:
            db.set_system_setting('landing_page_title', 'FLUX58 AI MEDIA LABS')
            db.set_system_setting('landing_page_subtitle', 'Powerful AI-Enhanced Video Editing')
            db.set_system_setting('landing_page_description', 
                                 'Create professional videos with our cloud-based video editor, powered by AI')
            db.set_system_setting('landing_page_hero_image', '/static/img/custom/openshot-banner.jpg')
            print("Initialized default landing page settings")
    except Exception as e:
        print(f"Error initializing landing page settings: {e}")
    
    return render_template('index.html', 
                          title=title, 
                          subtitle=subtitle, 
                          description=description,
                          hero_image=hero_image)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handle user login"""
    print("LOGIN PAGE ACCESSED")
    print(f"Method: {request.method}")
    print(f"Session before: {session}")
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt - Username: {username}, Password: {'*' * len(password)}")
        
        if not username or not password:
            print("Missing username or password")
            flash('Please provide both username and password', 'danger')
            return render_template('login.html')
        
        # Get user from database
        user = db.get_user_by_username(username)
        print(f"User from database: {user}")
        
        if not user:
            print("User not found in database")
            flash('Invalid credentials', 'danger')
            return render_template('login.html')
        
        # Check password
        password_valid = check_password_hash(user['password_hash'], password)
        print(f"Password hash from DB: {user['password_hash']}")
        print(f"Password valid: {password_valid}")
        
        if not password_valid:
            print("Password does not match")
            flash('Invalid credentials', 'danger')
            return render_template('login.html')
        
        # Store user info in session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']  # Store the role in the session
        
        print(f"Session after login: {session}")
        print(f"User role: {user['role']}")
        
        flash('Login successful!', 'success')
        
        # Redirect based on role
        if user['role'] == 'admin':
            print("Redirecting to admin dashboard")
            return redirect(url_for('admin_dashboard'))
        else:
            print("Redirecting to user dashboard")
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    """Handle user logout"""
    # Clear session
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'warning')
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    
    # Get user projects from database
    projects = project_manager.list_user_projects(user_id)
    
    # Get user credit information from database
    user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0, "transactions": []}
    
    # Get user's export jobs
    exports = db.list_user_exports(user_id) or []
    
    # Generate some activities based on real data
    activities = []
    
    # Add project creation activities
    for project in projects[:2]:  # Use up to 2 most recent projects
        activities.append({
            "icon": "bi-plus-circle",
            "description": f"Created project '{project['name']}'",
            "time": format_timestamp(project['created_at'])
        })
    
    # Add export activities
    for export in exports[:2]:  # Use up to 2 most recent exports
        activities.append({
            "icon": "bi-cloud-arrow-up",
            "description": f"Exported project (format: {export['format']})",
            "time": format_timestamp(export['started_at'])
        })
    
    # Sort activities by time (most recent first)
    activities.sort(key=lambda x: x["time"], reverse=True)
    
    # Format credit transactions for display
    transactions = []
    for tx in user_credits.get('transactions', [])[:5]:  # Show 5 most recent
        transactions.append({
            "amount": tx['amount'],
            "description": tx['description'] or ("Used credits" if tx['amount'] < 0 else "Added credits"),
            "time": format_timestamp(tx['timestamp'])
        })
    
    return render_template(
        'dashboard.html',
        projects=projects,
        credits=user_credits,
        exports=exports,
        activities=activities,
        transactions=transactions
    )

# Admin dashboard
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    # Get all users from database
    all_users = db.list_all_users()
    
    # Get all projects and organize by user
    all_projects = []
    user_projects = {}
    credits = {}
    
    for user in all_users:
        user_id = user['id']
        projects = project_manager.list_user_projects(user_id)
        all_projects.extend(projects)
        user_projects[user_id] = projects
        
        # Get credits for each user
        user_credits = db.get_user_credits(user_id)
        if user_credits:
            credits[user_id] = user_credits
    
    # Collect all export jobs from database
    # For simplicity, we'll just get exports from each user
    all_exports = []
    for user in all_users:
        user_exports = db.list_user_exports(user['id']) or []
        all_exports.extend(user_exports)
    
    # Calculate real system statistics
    total_storage = 0
    total_processing_time = 0
    project_sizes = []
    export_times = []
    
    # Calculate storage usage
    for project_id in os.listdir(project_manager.projects_path):
        project_dir = os.path.join(project_manager.projects_path, project_id)
        if os.path.isdir(project_dir):
            # Get directory size recursively
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(project_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            
            total_storage += total_size
            project_sizes.append(total_size / (1024 * 1024))  # Convert to MB
    
    # Calculate export processing times
    for export in all_exports:
        if export.get('completed_at') and export.get('started_at'):
            try:
                start = datetime.fromisoformat(export['started_at'])
                end = datetime.fromisoformat(export['completed_at'])
                duration = (end - start).total_seconds()
                total_processing_time += duration
                export_times.append(duration)
            except:
                pass
    
    # Create system stats object
    system_stats = {
        "storage": round(total_storage / (1024 * 1024), 2),  # Convert to MB
        "processing_time": round(total_processing_time / 60, 2),  # Convert to minutes
        "avg_project_size": round(sum(project_sizes) / len(project_sizes), 2) if project_sizes else 0,
        "avg_export_time": round(sum(export_times) / len(export_times), 2) if export_times else 0
    }
    
    # Generate recent activity based on real data
    recent_activity = []
    
    # Add user registrations
    for user in sorted(all_users, key=lambda x: x['created_at'], reverse=True)[:3]:
        recent_activity.append({
            "icon": "bi-person-plus",
            "description": f"New user registered: {user['username']}",
            "time": format_timestamp(user['created_at'])
        })
    
    # Add project creations
    for project in sorted(all_projects, key=lambda x: x['created_at'], reverse=True)[:3]:
        # Find username for this project
        username = "Unknown"
        for user in all_users:
            if user['id'] == project['user_id']:
                username = user['username']
                break
                
        recent_activity.append({
            "icon": "bi-film",
            "description": f"{username} created project: {project['name']}",
            "time": format_timestamp(project['created_at'])
        })
    
    # Add exports
    for export in sorted(all_exports, key=lambda x: x['started_at'], reverse=True)[:3]:
        # Find username for this export
        username = "Unknown"
        for user in all_users:
            if user['id'] == export['user_id']:
                username = user['username']
                break
                
        recent_activity.append({
            "icon": "bi-cloud-arrow-up",
            "description": f"{username} exported project (format: {export['format']})",
            "time": format_timestamp(export['started_at'])
        })
    
    # Sort activities by time (most recent first)
    recent_activity.sort(key=lambda x: x["time"], reverse=True)
    
    return render_template(
        'admin_dashboard.html',
        users=all_users,
        projects=all_projects,
        user_projects=user_projects,
        exports=all_exports,
        credits=credits,
        system_stats=system_stats,
        recent_activity=recent_activity
    )

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

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
'''

# Write the new file
with open(app_path, 'w') as f:
    f.write(simple_app)
print("Wrote new app.py with clean project routes")

print("\nProject routes created successfully!")
print("Run the following command to start the app in debug mode:")
print("cd /home/juanquy/OpenShot/test_app && python debug_app.py")