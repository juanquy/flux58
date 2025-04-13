#!/usr/bin/env python3
"""
FLUX58 AI MEDIA LABS - Application Routes
Routes for the FLUX58 video editing web application
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import (
    render_template, request, redirect, url_for, 
    session, flash, jsonify, send_from_directory, abort
)

# Check if we can import OpenShot
try:
    import openshot
    from openshot_api import openshot_api
    OPENSHOT_AVAILABLE = True
except ImportError:
    OPENSHOT_AVAILABLE = False

def admin_required(f):
    """Decorator to require admin role for a route"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'role' not in session:
            flash('You must be logged in as an admin to access this page.', 'error')
            return redirect(url_for('login_page'))
            
        if session['role'] != 'admin':
            flash('You must be an admin to access this page.', 'error')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    
    return decorated_function

def login_required(f):
    """Decorator to require login for a route"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to access this page.', 'error')
            return redirect(url_for('login_page'))
            
        return f(*args, **kwargs)
    
    return decorated_function

def register_routes(app, db, project_manager):
    """Register all routes for the application"""
    
    @app.route('/')
    def index():
        """Home page"""
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        """Login page"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please enter both username and password.', 'error')
                return render_template('login.html')
            
            # Get user from database
            user = db.get_user_by_username(username)
            
            if not user or not check_password_hash(user['password_hash'], password):
                flash('Invalid username or password.', 'error')
                return render_template('login.html')
            
            # Create session
            session_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=7)
            
            # Store session in database
            db.create_session_extended(
                token=session_token,
                user_id=user['id'],
                username=user['username'],
                expires_at=expires_at,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            # Store session in Flask
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['session_token'] = session_token
            session.permanent = True
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Logout"""
        if 'session_token' in session:
            db.delete_session(session['session_token'])
            
        # Clear Flask session
        session.clear()
        
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register page"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            
            if not username or not password or not email:
                flash('Please fill in all fields.', 'error')
                return render_template('register.html')
            
            # Check if username already exists
            existing_user = db.get_user_by_username(username)
            if existing_user:
                flash('Username already taken.', 'error')
                return render_template('register.html')
            
            # Create user
            user_id = str(uuid.uuid4())
            password_hash = generate_password_hash(password)
            
            success = db.create_user(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                email=email,
                role="user"
            )
            
            if success:
                # Add initial credits
                db.add_credits(
                    user_id=user_id,
                    amount=100,
                    transaction_type="initial",
                    description="Initial credits",
                    status="completed"
                )
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login_page'))
            else:
                flash('Error creating user. Please try again.', 'error')
                return render_template('register.html')
        
        return render_template('register.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard"""
        # Get user projects
        projects = project_manager.list_user_projects(session['user_id'])
        
        # Get user credits
        credits = db.get_user_credits(session['user_id'])
        
        return render_template(
            'dashboard.html', 
            username=session['username'],
            projects=projects,
            credits=credits
        )
    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        """Admin dashboard"""
        # Get all users
        users = db.list_all_users()
        
        # Get system settings
        settings = db.get_system_setting('app_settings', '{}')
        try:
            settings = json.loads(settings)
        except:
            settings = {}
        
        return render_template('admin_dashboard.html', users=users, settings=settings)
    
    @app.route('/admin/users')
    @admin_required
    def admin_users():
        """Admin users page"""
        users = db.list_all_users()
        return render_template('admin_users.html', users=users)
    
    @app.route('/admin/users/<user_id>')
    @admin_required
    def admin_edit_user(user_id):
        """Admin edit user page"""
        user = db.get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_users'))
            
        credits = db.get_user_credits(user_id)
        
        return render_template('admin_edit_user.html', user=user, credits=credits)
    
    @app.route('/admin/users/<user_id>/update', methods=['POST'])
    @admin_required
    def admin_update_user(user_id):
        """Admin update user"""
        email = request.form.get('email')
        role = request.form.get('role')
        
        if not email or not role:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('admin_edit_user', user_id=user_id))
        
        success = db.update_user(user_id=user_id, email=email, role=role)
        
        if success:
            flash('User updated successfully.', 'success')
        else:
            flash('Error updating user.', 'error')
            
        return redirect(url_for('admin_edit_user', user_id=user_id))
    
    @app.route('/admin/users/<user_id>/add_credits', methods=['POST'])
    @admin_required
    def admin_add_credits(user_id):
        """Admin add credits to user"""
        amount = request.form.get('amount')
        description = request.form.get('description', 'Added by admin')
        
        if not amount:
            flash('Please enter an amount.', 'error')
            return redirect(url_for('admin_edit_user', user_id=user_id))
        
        try:
            amount = int(amount)
        except:
            flash('Amount must be a number.', 'error')
            return redirect(url_for('admin_edit_user', user_id=user_id))
        
        if amount <= 0:
            flash('Amount must be positive.', 'error')
            return redirect(url_for('admin_edit_user', user_id=user_id))
        
        success = db.add_credits(
            user_id=user_id,
            amount=amount,
            transaction_type="admin",
            description=description,
            status="completed"
        )
        
        if success:
            flash(f'Added {amount} credits to user.', 'success')
        else:
            flash('Error adding credits.', 'error')
            
        return redirect(url_for('admin_edit_user', user_id=user_id))
    
    @app.route('/create_project', methods=['GET', 'POST'])
    @login_required
    def create_project():
        """Create a new project"""
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description', '')
            
            if not name:
                flash('Please enter a project name.', 'error')
                return render_template('create_project.html')
            
            # Create project
            try:
                project = project_manager.create_project(
                    user_id=session['user_id'],
                    project_name=name,
                    description=description
                )
                
                if project:
                    flash('Project created successfully.', 'success')
                    return redirect(url_for('project_details', project_id=project['id']))
                else:
                    flash('Error creating project.', 'error')
                    return render_template('create_project.html')
            except Exception as e:
                app.logger.error(f"Error creating project: {str(e)}")
                flash(f'Error creating project: {str(e)}', 'error')
                return render_template('create_project.html')
        
        return render_template('create_project.html')
    
    @app.route('/projects')
    @login_required
    def projects():
        """List user projects"""
        projects = project_manager.list_user_projects(session['user_id'])
        return render_template('projects.html', projects=projects)
    
    @app.route('/projects/<project_id>')
    @login_required
    def project_details(project_id):
        """View project details"""
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found.', 'error')
            return redirect(url_for('projects'))
        
        # Check if user is authorized
        if project['user_id'] != session['user_id'] and session['role'] != 'admin':
            flash('You are not authorized to view this project.', 'error')
            return redirect(url_for('projects'))
        
        return render_template('project_details.html', project=project)
    
    @app.route('/projects/<project_id>/delete', methods=['POST'])
    @login_required
    def delete_project(project_id):
        """Delete a project"""
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found.', 'error')
            return redirect(url_for('projects'))
        
        # Check if user is authorized
        if project['user_id'] != session['user_id'] and session['role'] != 'admin':
            flash('You are not authorized to delete this project.', 'error')
            return redirect(url_for('projects'))
        
        success = project_manager.delete_project(project_id)
        
        if success:
            flash('Project deleted successfully.', 'success')
        else:
            flash('Error deleting project.', 'error')
            
        return redirect(url_for('projects'))
    
    @app.route('/editor')
    @login_required
    def editor():
        """Editor page"""
        project_id = request.args.get('project_id')
        
        if not project_id:
            flash('No project selected.', 'error')
            return redirect(url_for('projects'))
        
        project = project_manager.get_project(project_id)
        
        if not project:
            flash('Project not found.', 'error')
            return redirect(url_for('projects'))
        
        # Check if user is authorized
        if project['user_id'] != session['user_id'] and session['role'] != 'admin':
            flash('You are not authorized to edit this project.', 'error')
            return redirect(url_for('projects'))
        
        # Check if OpenShot is available
        if not OPENSHOT_AVAILABLE:
            return render_template('editor_emergency.html', project=project)
        
        return render_template('editor.html', project=project)
    
    @app.route('/api/project/<project_id>')
    @login_required
    def api_get_project(project_id):
        """API endpoint to get project data"""
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Check if user is authorized
        if project['user_id'] != session['user_id'] and session['role'] != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Convert datetime objects to strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        return json.dumps({
            'success': True, 
            'project': project
        }, default=json_serializer)
    
    @app.route('/api/project/<project_id>/upload', methods=['POST'])
    @login_required
    def api_upload_asset(project_id):
        """API endpoint to upload an asset"""
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Check if user is authorized
        if project['user_id'] != session['user_id'] and session['role'] != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Get asset type
        asset_type = request.form.get('type', 'video')
        
        # Save file
        filename = secure_filename(file.filename)
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session['user_id'])
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Add asset to project
        try:
            asset = project_manager.add_asset(
                project_id=project_id,
                file_path=file_path,
                asset_type=asset_type,
                name=filename
            )
            
            if asset:
                return jsonify({
                    'success': True, 
                    'asset': asset
                })
            else:
                return jsonify({'success': False, 'error': 'Error adding asset'}), 500
        except Exception as e:
            app.logger.error(f"Error adding asset: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/project/<project_id>/timeline/add_clip', methods=['POST'])
    @login_required
    def api_add_clip(project_id):
        """API endpoint to add a clip to the timeline"""
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'success': False, 'error': 'Project not found'}), 404
        
        # Check if user is authorized
        if project['user_id'] != session['user_id'] and session['role'] != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        try:
            data = request.json
            
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            asset_id = data.get('asset_id')
            track_id = data.get('track_id')
            position = data.get('position')
            duration = data.get('duration')
            
            if not asset_id or not track_id or position is None or duration is None:
                return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
            
            # Add clip to timeline
            clip = project_manager.add_clip_to_timeline(
                project_id=project_id,
                asset_id=asset_id,
                track_id=track_id,
                position=float(position),
                duration=float(duration)
            )
            
            if clip:
                return jsonify({
                    'success': True, 
                    'clip': clip
                })
            else:
                return jsonify({'success': False, 'error': 'Error adding clip'}), 500
        except Exception as e:
            app.logger.error(f"Error adding clip: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/credits')
    @login_required
    def credits():
        """Credits page"""
        credits = db.get_user_credits(session['user_id'])
        return render_template('credits.html', credits=credits)
    
    @app.route('/buy_credits')
    @login_required
    def buy_credits():
        """Buy credits page"""
        return render_template('buy_credits.html')
    
    @app.route('/payment_success')
    @login_required
    def payment_success():
        """Payment success page"""
        # Add credits
        amount = int(request.args.get('amount', 100))
        
        success = db.add_credits(
            user_id=session['user_id'],
            amount=amount,
            transaction_type="purchase",
            description=f"Purchased {amount} credits",
            status="completed"
        )
        
        if success:
            flash(f'Added {amount} credits to your account.', 'success')
        else:
            flash('Error adding credits.', 'error')
            
        return render_template('payment_success.html', amount=amount)
    
    @app.route('/payment_cancel')
    @login_required
    def payment_cancel():
        """Payment cancel page"""
        return render_template('payment_cancel.html')
    
    @app.route('/pricing')
    def pricing():
        """Pricing page"""
        return render_template('pricing.html')
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500