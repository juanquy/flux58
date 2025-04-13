#!/usr/bin/env python3
import os
import uuid
import json
import shutil
from datetime import datetime
import mimetypes
from werkzeug.utils import secure_filename

print("Starting API Routes Update Script")

# 1. Backup app.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

# 2. Read app.py content
with open(app_path, 'r') as f:
    app_code = f.read()

# 3. Add API routes
# Find a good insertion point - add after existing imports
import_section_end = app_code.find("# Initialize Flask app")
if import_section_end == -1:
    import_section_end = app_code.find("app = Flask")

# Check if the route already exists to avoid duplicates
if "@app.route('/api/project/" not in app_code:
    # API routes to add
    api_routes = """
# API Routes for Editor Interface
@app.route('/api/project/<project_id>', methods=['GET'])
def api_get_project(project_id):
    \"\"\"Get project data for the editor\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get project data including timeline
        project_data = project_manager.get_project_data(project_id)
        
        # Get project assets
        assets = db.get_project_assets(project_id)
        
        # Combine project data with assets
        result = {
            'project': project_data,
            'assets': assets
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/project/<project_id>', methods=['PUT'])
def api_update_project(project_id):
    \"\"\"Update project data\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get request data
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update project data
        success = project_manager.update_project_data(project_id, data)
        
        if success:
            return jsonify({'success': True, 'message': 'Project updated'})
        else:
            return jsonify({'error': 'Failed to update project'}), 500
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/assets/upload', methods=['POST'])
def api_upload_asset():
    \"\"\"Upload a new asset\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    project_id = request.form.get('project_id')
    
    if not project_id:
        return jsonify({'error': 'Project ID is required'}), 400
    
    # Check if the project exists and user has access
    try:
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if the file type is allowed
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        allowed_extensions = []
        for extensions in app.config['ALLOWED_EXTENSIONS'].values():
            allowed_extensions.extend(extensions)
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save the file
        asset_id = str(uuid.uuid4())
        asset_dir = os.path.join(app.config['UPLOAD_FOLDER'], project_id)
        os.makedirs(asset_dir, exist_ok=True)
        
        file_path = os.path.join(asset_dir, f"{asset_id}.{file_ext}")
        file.save(file_path)
        
        # Determine asset type based on extension
        asset_type = None
        for type_name, extensions in app.config['ALLOWED_EXTENSIONS'].items():
            if file_ext in extensions:
                asset_type = type_name
                break
        
        # Add asset to database
        asset = {
            'id': asset_id,
            'project_id': project_id,
            'name': os.path.splitext(filename)[0],
            'type': asset_type,
            'file_extension': file_ext,
            'file_path': file_path,
            'created_at': datetime.now().isoformat()
        }
        
        db.add_asset(asset)
        
        # Generate thumbnail if it's a video or image
        if asset_type in ['video', 'image']:
            # In a real implementation, you'd call OpenShot API to generate a thumbnail
            # For now, we'll just report success
            asset['thumbnail_url'] = f"/assets/{asset_id}/thumbnail"
        
        return jsonify({
            'success': True, 
            'message': 'Asset uploaded', 
            'asset': asset
        })
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/assets/<asset_id>', methods=['DELETE'])
def api_delete_asset(asset_id):
    \"\"\"Delete an asset\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get asset from database
        asset = db.get_asset(asset_id)
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get the project
        project = project_manager.get_project(asset['project_id'])
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete the asset
        success = db.delete_asset(asset_id)
        
        if success:
            # Delete the file
            if os.path.exists(asset['file_path']):
                os.remove(asset['file_path'])
            
            return jsonify({'success': True, 'message': 'Asset deleted'})
        else:
            return jsonify({'error': 'Failed to delete asset'}), 500
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/assets/<asset_id>/enhance', methods=['POST'])
def api_enhance_asset(asset_id):
    \"\"\"Apply AI enhancement to an asset\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get asset from database
        asset = db.get_asset(asset_id)
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get the project
        project = project_manager.get_project(asset['project_id'])
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get enhancement type
        data = request.json
        if not data or 'enhancement_type' not in data:
            return jsonify({'error': 'Enhancement type is required'}), 400
        
        enhancement_type = data['enhancement_type']
        
        # Get user credits
        user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
        available_credits = user_credits["total"] - user_credits["used"]
        
        # Check if user has enough credits
        if enhancement_type == 'upscale' and available_credits < 5:
            return jsonify({'error': 'Not enough credits (5 required)'}), 402
        elif enhancement_type == 'noise_reduction' and available_credits < 3:
            return jsonify({'error': 'Not enough credits (3 required)'}), 402
        elif enhancement_type == 'color_correction' and available_credits < 2:
            return jsonify({'error': 'Not enough credits (2 required)'}), 402
        
        # This would be an async operation in reality, but for demo purposes:
        # In a real implementation, you'd call OpenShot API or an AI service
        # For now, we'll just report success and deduct credits
        
        # Deduct credits
        if enhancement_type == 'upscale':
            db.use_credits(user_id, 5)
        elif enhancement_type == 'noise_reduction':
            db.use_credits(user_id, 3)
        elif enhancement_type == 'color_correction':
            db.use_credits(user_id, 2)
        
        # Create a new enhanced asset
        enhanced_asset_id = str(uuid.uuid4())
        
        # In real implementation, this would be the enhanced file path
        original_path = asset['file_path']
        filename = os.path.basename(original_path)
        asset_dir = os.path.dirname(original_path)
        
        enhanced_filename = f"enhanced_{filename}"
        enhanced_path = os.path.join(asset_dir, enhanced_filename)
        
        # For demo, just copy the original file as the "enhanced" version
        shutil.copy2(original_path, enhanced_path)
        
        # Add the enhanced asset to database
        enhanced_asset = {
            'id': enhanced_asset_id,
            'project_id': asset['project_id'],
            'name': f"{asset['name']} (Enhanced)",
            'type': asset['type'],
            'file_extension': asset['file_extension'],
            'file_path': enhanced_path,
            'created_at': datetime.now().isoformat(),
            'enhancement_type': enhancement_type,
            'original_asset_id': asset_id
        }
        
        db.add_asset(enhanced_asset)
        
        return jsonify({
            'success': True, 
            'message': f'Asset enhanced with {enhancement_type}', 
            'asset': enhanced_asset
        })
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/exports', methods=['POST'])
def api_create_export():
    \"\"\"Create a new export job\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        project_id = data.get('project_id')
        export_format = data.get('format', 'mp4')
        resolution = data.get('resolution', '1080p')
        
        if not project_id:
            return jsonify({'error': 'Project ID is required'}), 400
        
        # Get project from database
        project = project_manager.get_project(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get user credits
        user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
        available_credits = user_credits["total"] - user_credits["used"]
        
        # Check if user has enough credits (10 for exports)
        if available_credits < 10:
            return jsonify({'error': 'Not enough credits (10 required)'}), 402
        
        # Create export job
        export_id = str(uuid.uuid4())
        export_dir = os.path.join('data', 'exports', project_id)
        os.makedirs(export_dir, exist_ok=True)
        
        export_filename = f"{project['name']}_{export_id}.{export_format}"
        export_path = os.path.join(export_dir, export_filename)
        
        export_job = {
            'id': export_id,
            'project_id': project_id,
            'user_id': user_id,
            'format': export_format,
            'resolution': resolution,
            'status': 'queued',
            'progress': 0,
            'file_path': export_path,
            'created_at': datetime.now().isoformat()
        }
        
        # Add export to database
        db.add_export(export_job)
        
        # Deduct credits
        db.use_credits(user_id, 10)
        
        # Add to export queue
        export_queue.add_export_job(export_job)
        
        return jsonify({
            'success': True, 
            'message': 'Export job created', 
            'export': export_job
        })
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/exports/<export_id>', methods=['GET'])
def api_get_export_status(export_id):
    \"\"\"Get export job status\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get export from database
        export_job = db.get_export(export_id)
        
        if not export_job:
            return jsonify({'error': 'Export job not found'}), 404
        
        # Check if user owns the export or is admin
        if export_job['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'export': export_job
        })
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500

@app.route('/api/assets/<asset_id>/download', methods=['GET'])
def api_download_asset(asset_id):
    \"\"\"Download an asset\"\"\"
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get asset from database
        asset = db.get_asset(asset_id)
        
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get the project
        project = project_manager.get_project(asset['project_id'])
        
        # Check if user owns the project or is admin
        if project['user_id'] != user_id and session.get('role') != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file exists
        if not os.path.exists(asset['file_path']):
            return jsonify({'error': 'File not found'}), 404
        
        # Guess the MIME type
        mime_type, _ = mimetypes.guess_type(asset['file_path'])
        
        # Send the file
        return send_file(
            asset['file_path'],
            mimetype=mime_type,
            as_attachment=True,
            attachment_filename=f"{asset['name']}.{asset['file_extension']}"
        )
    except Exception as e:
        print(f"API Error: {str(e)}")
        return jsonify({'error': 'Server error', 'message': str(e)}), 500
"""

    # Insert API routes at the appropriate location
    # Find where to add the route
    if "@app.route('/editor')" in app_code:
        editor_pos = app_code.find("@app.route('/editor')")
        editor_func_start = app_code.find("def editor_page", editor_pos)
        
        # Find the end of the function (next route or end of file)
        next_route_pos = len(app_code)
        for pos in range(editor_pos + 100, len(app_code) - 15):
            if app_code[pos:pos+11] == "@app.route(":
                next_route_pos = pos
                break
                
        # Add API routes after editor route
        new_app_code = app_code[:next_route_pos] + api_routes + app_code[next_route_pos:]
        app_code = new_app_code
        print("Added API routes for the editor")
    else:
        # If editor route not found, add to end of file
        app_code += api_routes
        print("Added API routes at the end of the file")
    
    # Add missing methods to database.py
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.py')
    with open(db_path, 'r') as f:
        db_code = f.read()
    
    # Check if methods already exist
    if "def add_asset(self, asset):" not in db_code:
        # Find a good insertion point - add after last method
        last_method_pos = db_code.rfind("def ")
        if last_method_pos != -1:
            # Find the end of the last method
            next_method_pos = db_code.find("def ", last_method_pos + 4)
            if next_method_pos == -1:
                # No more methods, add to end of file
                db_methods = """
    def add_asset(self, asset):
        \"\"\"Add a new asset to database\"\"\"
        try:
            query = \"\"\"
                INSERT INTO assets (id, project_id, name, type, file_extension, file_path, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            \"\"\"
            params = (
                asset['id'], 
                asset['project_id'], 
                asset['name'], 
                asset['type'], 
                asset['file_extension'], 
                asset['file_path'], 
                asset['created_at']
            )
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Database error: {str(e)}")
            return False
    
    def get_asset(self, asset_id):
        \"\"\"Get asset by ID\"\"\"
        try:
            query = \"\"\"
                SELECT * FROM assets WHERE id = %s
            \"\"\"
            params = (asset_id,)
            result = self.execute_query(query, params, fetch_one=True)
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None
    
    def get_project_assets(self, project_id):
        \"\"\"Get all assets for a project\"\"\"
        try:
            query = \"\"\"
                SELECT * FROM assets WHERE project_id = %s
                ORDER BY created_at DESC
            \"\"\"
            params = (project_id,)
            result = self.execute_query(query, params, fetch_all=True)
            return result or []
        except Exception as e:
            print(f"Database error: {str(e)}")
            return []
    
    def delete_asset(self, asset_id):
        \"\"\"Delete an asset\"\"\"
        try:
            query = \"\"\"
                DELETE FROM assets WHERE id = %s
            \"\"\"
            params = (asset_id,)
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Database error: {str(e)}")
            return False
    
    def add_export(self, export_job):
        \"\"\"Add a new export job to database\"\"\"
        try:
            query = \"\"\"
                INSERT INTO exports (id, project_id, user_id, format, resolution, status, progress, file_path, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            \"\"\"
            params = (
                export_job['id'], 
                export_job['project_id'], 
                export_job['user_id'], 
                export_job['format'], 
                export_job['resolution'], 
                export_job['status'], 
                export_job['progress'], 
                export_job['file_path'], 
                export_job['created_at']
            )
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Database error: {str(e)}")
            return False
    
    def get_export(self, export_id):
        \"\"\"Get export job by ID\"\"\"
        try:
            query = \"\"\"
                SELECT * FROM exports WHERE id = %s
            \"\"\"
            params = (export_id,)
            result = self.execute_query(query, params, fetch_one=True)
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")
            return None
    
    def update_export_status(self, export_id, status, progress=None):
        \"\"\"Update export job status\"\"\"
        try:
            if progress is not None:
                query = \"\"\"
                    UPDATE exports SET status = %s, progress = %s
                    WHERE id = %s
                \"\"\"
                params = (status, progress, export_id)
            else:
                query = \"\"\"
                    UPDATE exports SET status = %s
                    WHERE id = %s
                \"\"\"
                params = (status, export_id)
            
            self.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Database error: {str(e)}")
            return False
            """
            db_code += db_methods
            print("Added asset and export methods to database.py")
        else:
            print("Could not determine where to add methods in database.py")
    else:
        print("Asset and export methods already exist in database.py")
    
    # Write the updated code back to the files
    with open(app_path, 'w') as f:
        f.write(app_code)
        print("Saved changes to app.py")
    
    with open(db_path, 'w') as f:
        f.write(db_code)
        print("Saved changes to database.py")
    
    # Check if export_queue.py exists, if not create it
    export_queue_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'export_queue.py')
    if not os.path.exists(export_queue_path):
        export_queue_code = """
import threading
import time
import random
import os
from datetime import datetime

# Queue of export jobs
_export_queue = []
_queue_lock = threading.Lock()
_worker_thread = None
_running = False

def add_export_job(export_job):
    \"\"\"Add a job to the export queue\"\"\"
    global _export_queue, _worker_thread, _running
    
    with _queue_lock:
        _export_queue.append(export_job)
        
        # Start worker thread if not running
        if not _running:
            _running = True
            _worker_thread = threading.Thread(target=_process_queue)
            _worker_thread.daemon = True
            _worker_thread.start()

def _process_queue():
    \"\"\"Process jobs in the export queue\"\"\"
    global _export_queue, _running
    
    # Import database here to avoid circular imports
    from database import db
    
    try:
        while True:
            # Get next job
            job = None
            with _queue_lock:
                if _export_queue:
                    job = _export_queue.pop(0)
                else:
                    _running = False
                    break
            
            if job:
                # Update job status
                db.update_export_status(job['id'], 'processing', 0)
                
                # Simulate export process - this would call OpenShot API in reality
                total_steps = 20
                for step in range(total_steps + 1):
                    progress = int((step / total_steps) * 100)
                    
                    # Update progress in database
                    db.update_export_status(job['id'], 'processing', progress)
                    
                    # Simulate work
                    time.sleep(random.uniform(0.1, 0.5))
                
                # Create a dummy output file (in a real implementation, OpenShot would create the actual file)
                with open(job['file_path'], 'w') as f:
                    f.write(f"Simulated export for {job['project_id']} completed at {datetime.now().isoformat()}")
                
                # Mark job as completed
                db.update_export_status(job['id'], 'completed', 100)
                
                print(f"Export {job['id']} completed")
                
            # Small delay before checking for next job
            time.sleep(0.1)
    except Exception as e:
        print(f"Export worker error: {str(e)}")
        _running = False
"""
        with open(export_queue_path, 'w') as f:
            f.write(export_queue_code)
            print("Created export_queue.py")
    else:
        print("export_queue.py already exists")
    
    # Make sure required tables exist
    # Create database patch for assets and exports tables
    db_patch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'add_api_tables.py')
    db_patch_code = """#!/usr/bin/env python3
import os
import sys

# Import our custom modules - adjust as needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'postgres')

# Initialize database connection
logger.info(f"Connecting to database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
db = Database(host=DB_HOST, port=DB_PORT, 
              database=DB_NAME, user=DB_USER, password=DB_PASS)

# Create assets table if it doesn't exist
assets_table_query = \"\"\"
CREATE TABLE IF NOT EXISTS assets (
    id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    file_extension VARCHAR(20) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
\"\"\"

# Create exports table if it doesn't exist
exports_table_query = \"\"\"
CREATE TABLE IF NOT EXISTS exports (
    id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    format VARCHAR(20) NOT NULL,
    resolution VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    progress INTEGER NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
\"\"\"

try:
    # Create assets table
    db.execute_query(assets_table_query)
    logger.info("Assets table created or already exists")
    
    # Create exports table
    db.execute_query(exports_table_query)
    logger.info("Exports table created or already exists")
    
    logger.info("Database update complete!")
except Exception as e:
    logger.error(f"Error updating database: {str(e)}")
    sys.exit(1)
"""
    with open(db_patch_path, 'w') as f:
        f.write(db_patch_code)
        print("Created add_api_tables.py")

print("\nAPI routes update completed!")
print("To apply the database changes, run:")
print("python add_api_tables.py")
print("To restart the service, run:")
print("sudo systemctl restart openshot-web.service")