import os
import sys
import logging
import sys
import logging
import json
import uuid
from datetime import datetime
import shutil
from database import Database

# Project management class
class ProjectManager:
    def __init__(self, base_path='data'):
        self.projects_path = os.path.join(base_path, 'projects')
        self.exports_path = os.path.join(base_path, 'exports')
        
        # Ensure directories exist
        os.makedirs(self.projects_path, exist_ok=True)
        os.makedirs(self.exports_path, exist_ok=True)
        
        # Get the database instance from app.py if provided
        try:
            # First check module globals
            if 'db' in globals():
                self.db = db
            # Then check if this module has a db attribute (set from app.py)
            elif hasattr(sys.modules[__name__], 'db'):
                self.db = sys.modules[__name__].db
            # Otherwise raise an error - database connection is required
            else:
                print("Database connection not provided to ProjectManager, using DemoProjectManager")
                from database import DemoDatabase
                self.db = DemoDatabase()
                print("Using demo database for project manager")
        except Exception as e:
            print(f"Error setting up database for ProjectManager: {str(e)}")
            from database import DemoDatabase
            self.db = DemoDatabase()
            print("Using demo database for project manager due to error")
    
    def create_project(self, user_id, project_name, description=""):
        """Create a new OpenShot project"""
        project_id = str(uuid.uuid4())
        
        print(f"Creating project: ID={project_id}, Name={project_name}, User={user_id}")
        
        # Create project directory
        project_dir = os.path.join(self.projects_path, project_id)
        os.makedirs(project_dir, exist_ok=True)
        print(f"Project directory created: {project_dir}")
        
        # Create project in database
        try:
            print(f"Creating project in database with: ID={project_id}, User={user_id}, Name={project_name}")
            project = self.db.create_project(project_id, user_id, project_name, description)
            print(f"Database result: {project}")
            
            if not project:
                print("WARNING: Project creation in database failed!")
                # Clean up directory if database creation failed
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                return None
            
            # Create project file for OpenShot integration
            self._save_project_file(project_id, project)
            print(f"Project file saved successfully")
            
            return project
        except Exception as e:
            print(f"ERROR creating project: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Clean up directory if database creation failed
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return None
    
    def get_project(self, project_id):
        """Get a project by ID"""
        # Get project from database
        project = self.db.get_project(project_id)
        
        if not project:
            return None
        
        # Ensure project file exists
        if project:
            try:
                self._save_project_file(project_id, project)
            except Exception as e:
                print(f"Warning: Could not save project file: {str(e)}")
        
        return project
    
    def update_project(self, project_id, name=None, description=None):
        """Update project data"""
        # Update in database
        success = self.db.update_project(project_id, name, description)
        
        if not success:
            return None
        
        # Get updated project
        project = self.db.get_project(project_id)
        
        if project:
            # Update project file
            self._save_project_file(project_id, project)
        
        return project
    
    def delete_project(self, project_id):
        """Delete a project"""
        # Delete from database
        success = self.db.delete_project(project_id)
        
        if not success:
            return False
        
        # Delete project directory
        project_dir = os.path.join(self.projects_path, project_id)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        
        return True
    
    def list_user_projects(self, user_id):
        """List all projects for a user"""
        return self.db.list_user_projects(user_id)
    
    def add_asset(self, project_id, file_path, asset_type, name=None):
        """Add an asset to a project"""
        project = self.get_project(project_id)
        
        if not project:
            return None
        
        # Generate asset ID and filename
        asset_id = str(uuid.uuid4())
        filename = os.path.basename(file_path)
        
        if not name:
            name = filename
        
        # Copy file to project assets directory
        assets_dir = os.path.join(self.projects_path, project_id, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        target_path = os.path.join(assets_dir, f"{asset_id}_{filename}")
        shutil.copy2(file_path, target_path)
        
        # Add asset to database
        asset = self.db.add_asset(asset_id, project_id, name, filename, target_path, asset_type)
        
        # Update project file
        if asset:
            project = self.get_project(project_id)
            self._save_project_file(project_id, project)
        
        return asset
    
    def add_clip_to_timeline(self, project_id, asset_id, track_id, position, duration):
        """Add a clip to the timeline"""
        project = self.get_project(project_id)
        
        if not project:
            return None
        
        # Find the asset
        asset = None
        for a in project["assets"]:
            if a["id"] == asset_id:
                asset = a
                break
        
        if not asset:
            return None
        
        # Find or create track
        track = None
        track_exists = False
        
        # Look for track in project
        for t in project["timeline"]["tracks"]:
            if t["id"] == track_id:
                track = t
                track_exists = True
                break
        
        # If track doesn't exist, create it
        if not track:
            track_name = f"Track {len(project['timeline']['tracks']) + 1}"
            track = self.db.add_track(track_id, project_id, track_name)
            
            if not track:
                return None
        
        # Create clip
        clip_id = str(uuid.uuid4())
        clip = self.db.add_clip(
            clip_id=clip_id,
            track_id=track_id,
            asset_id=asset_id,
            position=position,
            duration=duration
        )
        
        if clip:
            # Update project file
            project = self.get_project(project_id)
            self._save_project_file(project_id, project)
        
        return clip
    
    def _save_project_file(self, project_id, project_data):
        """Save project data to file"""
        try:
            project_dir = os.path.join(self.projects_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            project_file = os.path.join(project_dir, "project.json")
            
            # Create a clean copy of project data for OpenShot
            openshot_project = {
                "id": project_data.get("id", project_id),
                "name": project_data.get("name", "Untitled Project"),
                "description": project_data.get("description", ""),
                "user_id": project_data.get("user_id", ""),
                "created_at": project_data.get("created_at", datetime.now().isoformat()),
                "updated_at": project_data.get("updated_at", datetime.now().isoformat()),
                "assets": [],
                "timeline": project_data.get("timeline", {
                    "duration": 60,
                    "width": 1920,
                    "height": 1080,
                    "fps": {
                        "num": 30,
                        "den": 1
                    },
                    "sample_rate": 48000,
                    "channels": 2,
                    "channel_layout": 3,
                    "tracks": []
                })
            }
            
            # Ensure timeline has proper structure
            if not isinstance(openshot_project["timeline"], dict):
                openshot_project["timeline"] = {
                    "duration": 60,
                    "width": 1920,
                    "height": 1080,
                    "fps": {"num": 30, "den": 1},
                    "sample_rate": 48000,
                    "channels": 2,
                    "channel_layout": 3,
                    "tracks": []
                }
            
            # Ensure timeline tracks exists and is a list
            if "tracks" not in openshot_project["timeline"] or not isinstance(openshot_project["timeline"]["tracks"], list):
                openshot_project["timeline"]["tracks"] = []
            
            # Process assets to make sure file paths are correct
            if project_data.get("assets") and isinstance(project_data.get("assets"), list):
                for asset in project_data.get("assets", []):
                    if not isinstance(asset, dict):
                        continue
                        
                    asset_copy = dict(asset)
                    
                    # Ensure asset path is accessible to OpenShot
                    if "path" in asset_copy and not os.path.exists(asset_copy["path"]):
                        # Try to fix path if it's a relative path
                        if "id" in asset_copy and "filename" in asset_copy:
                            potential_path = os.path.join(project_dir, "assets", 
                                                        f"{asset_copy['id']}_{asset_copy['filename']}")
                            if os.path.exists(potential_path):
                                asset_copy["path"] = potential_path
                    
                    openshot_project["assets"].append(asset_copy)
            
            # Make sure all clips have reference to asset paths for export
            for track in openshot_project["timeline"].get("tracks", []):
                if isinstance(track, dict) and "clips" in track and isinstance(track["clips"], list):
                    for clip in track.get("clips", []):
                        if not isinstance(clip, dict):
                            continue
                            
                        # Find associated asset for this clip
                        asset_id = clip.get("asset_id")
                        if asset_id:
                            for asset in openshot_project["assets"]:
                                if asset.get("id") == asset_id:
                                    clip["asset_path"] = asset.get("path", "")
                                    break
            
            # Convert datetime objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
                
            # Save to file
            with open(project_file, 'w') as f:
                json.dump(openshot_project, f, indent=2, default=json_serializer)
                
            print(f"Project file saved successfully: {project_file}")
            
        except Exception as e:
            print(f"Error saving project file: {str(e)}")
            import traceback
            print(traceback.format_exc())