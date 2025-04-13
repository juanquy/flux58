import os
import threading
import time
import traceback
from datetime import datetime
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import OpenShot API
try:
    from openshot_api import OpenShotAPI
    logger.info("Successfully imported OpenShotAPI")
except ImportError as e:
    logger.error(f"Error importing OpenShotAPI: {e}")
    # Create a dummy OpenShotAPI class for fallback
    class OpenShotAPI:
        def __init__(self):
            self.available = False
            
        def get_status(self):
            return {
                "available": False,
                "version": "0.0.0",
                "message": "OpenShot API not available",
                "capabilities": {
                    "video_editing": False,
                    "audio_editing": False,
                    "rendering": False,
                    "effects": False
                }
            }

# Global variables
queue_processor = None
max_concurrent_exports = 2  # Maximum number of concurrent exports
active_exports = {}  # Dictionary to track active exports (export_id -> thread)
queue_lock = threading.Lock()  # Lock for thread-safe operations
stop_flag = threading.Event()  # Event to signal processor to stop

class ExportQueue:
    """
    Export queue for managing video export tasks
    """
    def __init__(self, db_connection):
        self.db = db_connection
        self.api = OpenShotAPI()
        
    def add_export_task(self, project_id, user_id, export_settings):
        """
        Add a new export task to the queue
        """
        try:
            # Generate export ID
            export_id = f"export_{int(time.time())}_{project_id}"
            
            # Create output file name
            file_name = export_settings.get("file_name", f"export_{project_id}_{int(time.time())}.mp4")
            output_path = os.path.join("data", "exports", file_name)
            
            # Ensure exports directory exists
            os.makedirs(os.path.join("data", "exports"), exist_ok=True)
            
            # Add to database queue
            cursor = self.db.cursor()
            cursor.execute(
                """
                INSERT INTO export_queue 
                (id, project_id, user_id, status, output_path, settings, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    export_id,
                    project_id,
                    user_id,
                    "queued",
                    output_path,
                    export_settings,
                    datetime.now()
                )
            )
            self.db.commit()
            
            return export_id
        except Exception as e:
            logger.error(f"Error adding export task: {str(e)}")
            traceback.print_exc()
            return None
    
    def process_queue(self):
        """
        Process queued export tasks
        """
        try:
            # Get queued exports
            cursor = self.db.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT * FROM export_queue
                WHERE status = 'queued'
                ORDER BY created_at ASC
                LIMIT %s
                """,
                (max_concurrent_exports - len(active_exports),)
            )
            queued_exports = cursor.fetchall()
            
            # Process each queued export
            for export in queued_exports:
                # Check if we can process more exports
                if len(active_exports) >= max_concurrent_exports:
                    break
                
                # Update status to processing
                cursor.execute(
                    """
                    UPDATE export_queue
                    SET status = 'processing', started_at = %s
                    WHERE id = %s
                    """,
                    (datetime.now(), export["id"])
                )
                self.db.commit()
                
                # Start export in a new thread
                export_thread = threading.Thread(
                    target=self._export_worker,
                    args=(export,)
                )
                export_thread.daemon = True
                export_thread.start()
                
                # Add to active exports
                with queue_lock:
                    active_exports[export["id"]] = export_thread
                
                logger.info(f"Started export {export['id']} for project {export['project_id']}")
        except Exception as e:
            logger.error(f"Error processing export queue: {str(e)}")
            traceback.print_exc()
    
    def _export_worker(self, export):
        """
        Worker function to export video
        """
        try:
            # Simulate export
            logger.info(f"Exporting project {export['project_id']} to {export['output_path']}")
            
            # Update progress
            self._update_export_progress(export["id"], 10)
            time.sleep(2)  # Simulate work
            
            # Update progress
            self._update_export_progress(export["id"], 50)
            time.sleep(3)  # Simulate work
            
            # Complete export
            cursor = self.db.cursor()
            cursor.execute(
                """
                UPDATE export_queue
                SET status = 'completed', completed_at = %s, progress = 100
                WHERE id = %s
                """,
                (datetime.now(), export["id"])
            )
            self.db.commit()
            
            logger.info(f"Export {export['id']} completed")
        except Exception as e:
            # Update status to failed
            cursor = self.db.cursor()
            cursor.execute(
                """
                UPDATE export_queue
                SET status = 'failed', error_message = %s
                WHERE id = %s
                """,
                (str(e), export["id"])
            )
            self.db.commit()
            
            logger.error(f"Export {export['id']} failed: {str(e)}")
            traceback.print_exc()
        finally:
            # Remove from active exports
            with queue_lock:
                if export["id"] in active_exports:
                    del active_exports[export["id"]]
    
    def _update_export_progress(self, export_id, progress):
        """
        Update export progress in database
        """
        cursor = self.db.cursor()
        cursor.execute(
            """
            UPDATE export_queue
            SET progress = %s
            WHERE id = %s
            """,
            (progress, export_id)
        )
        self.db.commit()

def start_queue_processor(db_connection):
    """
    Start the export queue processor
    """
    global queue_processor, stop_flag
    
    if queue_processor is not None and queue_processor.is_alive():
        return  # Already running
    
    # Reset stop flag
    stop_flag.clear()
    
    # Create export queue
    export_queue = ExportQueue(db_connection)
    
    # Define processor function
    def processor_thread():
        while not stop_flag.is_set():
            try:
                # Process queue
                export_queue.process_queue()
                
                # Sleep before next check
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in queue processor: {str(e)}")
                traceback.print_exc()
                time.sleep(10)  # Sleep longer on error
    
    # Start processor thread
    queue_processor = threading.Thread(target=processor_thread)
    queue_processor.daemon = True
    queue_processor.start()
    
    logger.info("Export queue processor started")

def stop_queue_processor():
    """
    Stop the export queue processor
    """
    global stop_flag
    
    # Set stop flag
    stop_flag.set()
    
    logger.info("Export queue processor stopping")