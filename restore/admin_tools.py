import os
import json
import time
import datetime
import shutil
import logger

class AdminTools:
    def __init__(self, database, backup_dir='backups'):
        """Initialize admin tools with database connection"""
        self.db = database
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def backup_database(self):
        """Create a backup of the PostgreSQL database"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_dir, f"flux58_db_{timestamp}.sql")
        
        logger.info(f"Creating database backup to {backup_path}")
        
        try:
            result = self.db.backup_database(backup_path)
            
            if result:
                # Record backup in system settings
                self.db.set_system_setting('last_backup_time', timestamp)
                self.db.set_system_setting('last_backup_path', backup_path)
                
                logger.info("Database backup successful")
                return {
                    "success": True,
                    "backup_path": backup_path,
                    "timestamp": timestamp,
                    "file_size": os.path.getsize(backup_path)
                }
            else:
                logger.error("Database backup failed")
                return {
                    "success": False,
                    "error": "Backup operation failed"
                }
        except Exception as e:
            logger.error(f"Error during database backup: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self):
        """List all available database backups"""
        backups = []
        
        # List all backup files
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('flux58_db_') and filename.endswith('.sql'):
                    filepath = os.path.join(self.backup_dir, filename)
                    
                    # Extract timestamp from filename
                    timestamp_str = filename[10:-4]  # Remove "flux58_db_" and ".sql"
                    
                    try:
                        # Parse timestamp
                        timestamp = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                        
                        # Get file info
                        stat = os.stat(filepath)
                        file_size = stat.st_size
                        file_mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                        
                        backups.append({
                            "filename": filename,
                            "path": filepath,
                            "timestamp": timestamp,
                            "size": file_size,
                            "modified_time": file_mtime
                        })
                    except ValueError:
                        # Skip files that don't match the naming pattern
                        pass
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return backups
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
            return []
    
    def restore_database(self, backup_path):
        """Restore database from a backup file"""
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return {
                "success": False,
                "error": "Backup file not found"
            }
        
        try:
            # For PostgreSQL, use the pg_db's restore method
            return self.db.pg_db.restore_database(backup_path)
        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_database_stats(self):
        """Get database statistics"""
        # For PostgreSQL, use the dedicated method
        return self.db.pg_db.get_database_stats()
    
    def get_system_status(self):
        """Get overall system status"""
        status = {
            "storage": {},
            "database": {},
            "exports": {}
        }
        
        # Get storage information
        try:
            # Storage for project data
            projects_dir = os.path.join('data', 'projects')
            if os.path.exists(projects_dir):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(projects_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                
                status["storage"]["projects"] = {
                    "size": total_size,
                    "file_count": file_count
                }
            
            # Storage for exports
            exports_dir = os.path.join('data', 'exports')
            if os.path.exists(exports_dir):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(exports_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                
                status["storage"]["exports"] = {
                    "size": total_size,
                    "file_count": file_count
                }
            
            # Storage for uploads
            uploads_dir = os.path.join('data', 'uploads')
            if os.path.exists(uploads_dir):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(uploads_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                
                status["storage"]["uploads"] = {
                    "size": total_size,
                    "file_count": file_count
                }
            
            # Storage for backups
            if os.path.exists(self.backup_dir):
                total_size = 0
                file_count = 0
                
                for root, dirs, files in os.walk(self.backup_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                
                status["storage"]["backups"] = {
                    "size": total_size,
                    "file_count": file_count
                }
            
            # Database info from PostgreSQL
            db_stats = self.db.pg_db.get_database_stats()
            status["database"] = db_stats
            
            # Export queue info from PostgreSQL
            export_stats = self.db.pg_db.get_export_stats()
            status["exports"]["status_counts"] = export_stats
            
            return status
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def cleanup_old_data(self, days=30):
        """Clean up old data to free up space"""
        results = {
            "logs_deleted": 0,
            "exports_deleted": 0,
            "temp_files_deleted": 0
        }
        
        try:
            # Clean up old logs
            logs_deleted = self.db.clear_old_logs(days)
            results["logs_deleted"] = logs_deleted
            
            # Clean up old exports (completed more than X days ago)
            # Get list of old export files to delete from PostgreSQL
            old_exports = self.db.pg_db.get_old_exports(days)
            
            # Delete the export files
            for export_id, output_path in old_exports:
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                        results["exports_deleted"] += 1
                except Exception as e:
                    logger.warning(f"Failed to delete export file {output_path}: {str(e)}")
            
            # Clean up temp files in uploads directory
            uploads_dir = os.path.join('data', 'uploads')
            if os.path.exists(uploads_dir):
                # Get list of files older than X days
                cutoff_time = time.time() - (days * 86400)
                
                for filename in os.listdir(uploads_dir):
                    file_path = os.path.join(uploads_dir, filename)
                    
                    if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            results["temp_files_deleted"] += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")
            
            logger.info(f"Cleanup completed: {results}")
            return results
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def vacuum_database(self):
        """Run VACUUM on database to optimize storage"""
        # For PostgreSQL, use the dedicated method
        return self.db.pg_db.vacuum_database()