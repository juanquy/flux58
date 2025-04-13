import json
import os
import logging
import sys
from datetime import datetime, timedelta

# Check if psycopg2 is available
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
    logging.info("PostgreSQL support is available")
except ImportError:
    POSTGRES_AVAILABLE = False
    logging.error("PostgreSQL support not available - psycopg2 not installed")

try:
    from postgres_db import PostgresDatabase
    POSTGRES_DB_AVAILABLE = True
    logging.info("PostgreSQL database module loaded successfully")
except ImportError as e:
    POSTGRES_DB_AVAILABLE = False
    logging.error(f"Error importing PostgresDatabase: {str(e)}")

# Define a DemoDatabase class for testing
class DemoDatabase:
    """Simple in-memory database for demo/testing"""
    def __init__(self):
        self.users = {
            "admin": {
                "id": "admin-uuid",
                "username": "admin",
                "password_hash": "admin-hash",
                "email": "admin@example.com",
                "role": "admin",
                "created_at": datetime.now()
            }
        }
        self.projects = {}
        self.assets = {}
        self.exports = {}
        self.settings = {}
        self.credits = {"admin-uuid": {"total": 1000, "used": 0, "transactions": []}}
        self.logs = []
        
    def get_user_by_username(self, username):
        return self.users.get(username)
        
    def list_all_users(self):
        return list(self.users.values())
        
    def get_user_credits(self, user_id):
        return self.credits.get(user_id)
        
    def get_system_setting(self, name, default=None):
        print(f"DEBUG: Getting demo system setting {name}, current settings: {self.settings}")
        return self.settings.get(name, default)
        
    def set_system_setting(self, name, value):
        print(f"DEBUG: Setting demo system setting {name} = {value}")
        self.settings[name] = value
        return True
        
    def get_all_system_settings(self):
        print(f"DEBUG: Getting all demo system settings: {self.settings}")
        return self.settings.copy()
        
    def cleanup_expired_sessions(self):
        pass
        
    def create_user(self, **kwargs):
        user_id = kwargs.get('user_id')
        self.users[kwargs.get('username')] = kwargs
        return user_id
        
    def add_credits(self, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id not in self.credits:
            self.credits[user_id] = {"total": 0, "used": 0, "transactions": []}
        self.credits[user_id]["total"] += kwargs.get('amount', 0)
        tx = {
            "amount": kwargs.get('amount', 0),
            "description": kwargs.get('description', ''),
            "timestamp": datetime.now()
        }
        self.credits[user_id]["transactions"].append(tx)
        return True
        
    def get_project_assets(self, project_id):
        return self.assets.get(project_id, [])
        
    def add_log(self, level, message, source=None, user_id=None, ip_address=None, request_path=None):
        """Add a log entry"""
        log_entry = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message,
            "source": source,
            "user_id": user_id,
            "ip_address": ip_address,
            "request_path": request_path
        }
        self.logs.append(log_entry)
        print(f"LOG: [{level}] {message}")
        return True
        
    def list_user_exports(self, user_id):
        """List exports for a user"""
        return []
        
    def add_export(self, project_id, export_id, export_data):
        """Add export data"""
        return True
        
    def add_asset(self, asset):
        """Add an asset"""
        project_id = asset.get('project_id')
        if project_id not in self.assets:
            self.assets[project_id] = []
        self.assets[project_id].append(asset)
        return True
        
    def get_asset(self, asset_id):
        """Get an asset by ID"""
        for project_assets in self.assets.values():
            for asset in project_assets:
                if asset.get('id') == asset_id:
                    return asset
        return None
        
    def delete_asset(self, asset_id):
        """Delete an asset"""
        for project_id, project_assets in self.assets.items():
            for i, asset in enumerate(project_assets):
                if asset.get('id') == asset_id:
                    del self.assets[project_id][i]
                    return True
        return False

class Database:
    def __init__(self, db_path=None, use_postgres=True, 
                 host='localhost', port=5432, database='flux58',
                 user='postgres', password='postgres'):
        """Initialize database with PostgreSQL backend"""
        self.use_postgres = True  # Always use PostgreSQL
        
        try:
            # Use PostgreSQL as the database backend if available
            if POSTGRES_AVAILABLE and POSTGRES_DB_AVAILABLE:
                self.pg_db = PostgresDatabase(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
                print("Using PostgreSQL database")
            else:
                raise ImportError("PostgreSQL support not available")
        except Exception as e:
            # Fall back to demo database
            print(f"Warning: OpenShot library not found, using placeholder implementation")
            self.pg_db = DemoDatabase()
            self.use_postgres = False
            print("Using demo project manager for testing")
    
    # Connection management - act as pass-through to PostgreSQL
    def _connect(self):
        """Connect to database - no-op for PostgreSQL"""
        pass
    
    def _disconnect(self):
        """Disconnect from database - no-op for PostgreSQL"""
        pass
    
    def _initialize_db(self):
        """Initialize database tables - handled by PostgresDatabase"""
        pass
    
    # All methods below are pass-through to PostgreSQL implementation
    
    # User Management Methods
    def create_user(self, user_id, username, password_hash, email, role="user"):
        """Create a new user"""
        return self.pg_db.create_user(user_id, username, password_hash, email, role)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return self.pg_db.get_user_by_username(username)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.pg_db.get_user_by_id(user_id)
    
    def update_user(self, user_id, email=None, password_hash=None, role=None):
        """Update user details"""
        return self.pg_db.update_user(user_id, email, password_hash, role)
    
    def delete_user(self, user_id):
        """Delete user"""
        return self.pg_db.delete_user(user_id)
    
    def list_all_users(self):
        """List all users"""
        return self.pg_db.list_all_users()
    
    # Session Management Methods
    def create_session(self, token, user_id, username, expires_at):
        """Create a new session"""
        return self.pg_db.create_session(token, user_id, username, expires_at)
    
    def get_session(self, token):
        """Get session by token"""
        return self.pg_db.get_session(token)
    
    def delete_session(self, token):
        """Delete session"""
        return self.pg_db.delete_session(token)
    
    def cleanup_expired_sessions(self):
        """Delete expired sessions"""
        return self.pg_db.cleanup_expired_sessions()
    
    # Credit Management Methods
    def get_user_credits(self, user_id):
        """Get user's credit information"""
        return self.pg_db.get_user_credits(user_id)
    
    def add_credits(self, user_id, amount, transaction_type, description="", status="completed"):
        """Add credits to user account"""
        return self.pg_db.add_credits(user_id, amount, transaction_type, description, status)
    
    def use_credits(self, user_id, amount, description="", transaction_type="usage", status="completed"):
        """Use credits from user account"""
        return self.pg_db.use_credits(user_id, amount, description, transaction_type, status)
    
    # Project Management Methods
    def create_project(self, project_id, user_id, name, description=""):
        """Create a new project"""
        return self.pg_db.create_project(project_id, user_id, name, description)
    
    def get_project(self, project_id):
        """Get project by ID including all related data"""
        return self.pg_db.get_project(project_id)
    
    def update_project(self, project_id, name=None, description=None):
        """Update project metadata"""
        return self.pg_db.update_project(project_id, name, description)
    
    def delete_project(self, project_id):
        """Delete project and all related data"""
        return self.pg_db.delete_project(project_id)
    
    def list_user_projects(self, user_id):
        """List projects for a user"""
        return self.pg_db.list_user_projects(user_id)
    
    # Asset Management Methods
    def add_asset(self, asset):
        """Add an asset to a project"""
        if not isinstance(asset, dict):
            return None
        
        asset_id = asset.get('id')
        project_id = asset.get('project_id')
        name = asset.get('name')
        path = asset.get('path')
        asset_type = asset.get('type')
        
        if not all([asset_id, project_id, name, path, asset_type]):
            return None
        
        # Extract filename from path
        filename = os.path.basename(path)
        
        return self.pg_db.add_asset(asset_id, project_id, name, filename, path, asset_type)
    
    def get_asset(self, asset_id):
        """Get asset by ID"""
        return self.pg_db.get_asset(asset_id)
        
    def get_project_assets(self, project_id):
        """Get all assets for a project"""
        try:
            # Pass through to PostgreSQL implementation
            conn, cursor = self.pg_db._get_connection()
            cursor.execute(
                "SELECT * FROM project_assets WHERE project_id = %s",
                (project_id,)
            )
            
            assets = []
            for row in cursor.fetchall():
                # Convert row to dict
                asset = dict(row)
                assets.append(asset)
            
            return assets
        except Exception as e:
            logging.error(f"Error getting project assets: {str(e)}")
            return []
            
    def delete_asset(self, asset_id):
        """Delete an asset"""
        try:
            # Pass through to PostgreSQL implementation
            conn, cursor = self.pg_db._get_connection()
            cursor.execute(
                "DELETE FROM project_assets WHERE id = %s",
                (asset_id,)
            )
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting asset: {str(e)}")
            return False
            
    def add_export(self, project_id, export_id, export_data):
        """Add an export to the database"""
        try:
            # Extract data from export_data
            if not isinstance(export_data, dict):
                return False
                
            output_path = export_data.get('output_path')
            format = export_data.get('format', 'mp4')
            width = export_data.get('width', 1920)
            height = export_data.get('height', 1080)
            fps = export_data.get('fps', 30)
            video_bitrate = export_data.get('video_bitrate', '8000k')
            audio_bitrate = export_data.get('audio_bitrate', '192k')
            
            # Get user_id from project
            project = self.get_project(project_id)
            if not project:
                return False
                
            user_id = project.get('user_id')
            
            # Create export job
            return self.pg_db.create_export_job(
                export_id, project_id, user_id, output_path, format,
                width, height, fps, video_bitrate, audio_bitrate
            )
        except Exception as e:
            logging.error(f"Error adding export: {str(e)}")
            return False
    
    # Timeline Management Methods
    def add_track(self, track_id, project_id, name):
        """Add a track to a project timeline"""
        return self.pg_db.add_track(track_id, project_id, name)
    
    def add_clip(self, clip_id, track_id, asset_id, position, duration, start=0, end=None, properties=None):
        """Add a clip to a timeline track"""
        return self.pg_db.add_clip(clip_id, track_id, asset_id, position, duration, start, end, properties)
    
    # Export Management Methods
    def create_export_job(self, export_id, project_id, user_id, output_path, 
                          format="mp4", width=1920, height=1080, fps=30,
                          video_bitrate="8000k", audio_bitrate="192k",
                          start_frame=1, end_frame=None):
        """Create a new export job"""
        return self.pg_db.create_export_job(
            export_id, project_id, user_id, output_path, format, 
            width, height, fps, video_bitrate, audio_bitrate,
            start_frame, end_frame
        )
    
    def update_export_status(self, export_id, status, completed_at=None):
        """Update export job status"""
        return self.pg_db.update_export_status(export_id, status, completed_at)
    
    def get_export_job(self, export_id):
        """Get export job by ID"""
        return self.pg_db.get_export_job(export_id)
    
    def list_user_exports(self, user_id):
        """List export jobs for a user"""
        return self.pg_db.list_user_exports(user_id)
    
    # Session Management Extensions
    def create_session_extended(self, token, user_id, username, expires_at, ip_address=None, user_agent=None):
        """Create a new session with extended information"""
        return self.pg_db.create_session_extended(token, user_id, username, expires_at, ip_address, user_agent)
    
    def update_session_activity(self, token, ip_address=None):
        """Update session last activity time"""
        return self.pg_db.update_session_activity(token, ip_address)
    
    def get_user_sessions(self, user_id):
        """Get all active sessions for a user"""
        return self.pg_db.get_user_sessions(user_id)
    
    def invalidate_all_user_sessions(self, user_id, except_token=None):
        """Invalidate all sessions for a user except the current one"""
        return self.pg_db.invalidate_all_user_sessions(user_id, except_token)
    
    # Export Queue System
    def create_export_job_with_priority(self, export_id, project_id, user_id, output_path, 
                                       format="mp4", width=1920, height=1080, fps=30,
                                       video_bitrate="8000k", audio_bitrate="192k",
                                       start_frame=1, end_frame=None, priority=0):
        """Create a new export job with priority"""
        return self.pg_db.create_export_job_with_priority(
            export_id, project_id, user_id, output_path, format, 
            width, height, fps, video_bitrate, audio_bitrate,
            start_frame, end_frame, priority
        )
    
    def update_export_progress(self, export_id, progress, status=None):
        """Update export job progress"""
        return self.pg_db.update_export_progress(export_id, progress, status)
    
    def get_next_pending_export(self):
        """Get the next pending export job with highest priority"""
        return self.pg_db.get_next_pending_export()
    
    def cancel_export_job(self, export_id):
        """Cancel an export job"""
        return self.pg_db.cancel_export_job(export_id)
    
    def get_active_exports(self):
        """Get all currently processing export jobs"""
        return self.pg_db.get_active_exports()
    
    # Logging System
    def add_log(self, level, module, message, user_id=None, ip_address=None):
        """Add a log entry to the system log"""
        return self.pg_db.add_log(level, module, message, user_id, ip_address)
    
    def get_logs(self, limit=100, offset=0, level=None, module=None, user_id=None):
        """Get system logs with filtering options"""
        return self.pg_db.get_logs(limit, offset, level, module, user_id)
    
    def clear_old_logs(self, days=30):
        """Clear logs older than specified days"""
        return self.pg_db.clear_old_logs(days)
    
    # System Settings
    def set_system_setting(self, key, value):
        """Set or update a system setting"""
        return self.pg_db.set_system_setting(key, value)
    
    def get_system_setting(self, key, default=None):
        """Get a system setting value"""
        return self.pg_db.get_system_setting(key, default)
    
    def get_all_system_settings(self):
        """Get all system settings"""
        return self.pg_db.get_all_system_settings()
    
    def backup_database(self, backup_path):
        """Create a backup of the database"""
        backup_result = self.pg_db.backup_database()
        
        # If backup was successful and we want to store it at a specific path,
        # we could copy the file from the default location
        if backup_result.get('success') and 'file' in backup_result:
            import shutil
            shutil.copy2(backup_result['file'], backup_path)
        
        return backup_result.get('success', False)