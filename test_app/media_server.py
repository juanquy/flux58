#!/usr/bin/env python3
"""
Media Server routes for Flux58

This script adds routes to serve media files directly from the uploads directory
"""
import os
import sys
import mimetypes
from flask import Flask, send_from_directory, abort, session, jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_media_routes(app, db_connection=None):
    """Add media routes to the Flask app"""
    
    # Get the uploads directory from the app config or use default
    UPLOAD_FOLDER = getattr(app, 'config', {}).get('UPLOAD_FOLDER', 
                                                  os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                              'data', 'uploads'))
    
    logger.info(f"Adding media routes for upload folder: {UPLOAD_FOLDER}")
    
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """Serve files from the uploads directory"""
        try:
            # Basic security check - make sure there are no parent directory traversals
            if '..' in filename:
                abort(403)  # Forbidden
            
            # Simple auth check - user must be logged in 
            # (You might want to enhance this further)
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Get the file extension for MIME type detection
            _, ext = os.path.splitext(filename)
            
            # Special handling for video files
            if ext.lower() in ['.mp4', '.webm', '.mov', '.avi']:
                # Set video-specific headers for proper streaming
                headers = {
                    'Accept-Ranges': 'bytes',
                    'Cache-Control': 'public, max-age=3600'
                }
                
                return send_from_directory(UPLOAD_FOLDER, filename, 
                                         mimetype=mimetypes.guess_type(filename)[0],
                                         as_attachment=False,
                                         conditional=True,
                                         download_name=None,
                                         headers=headers)
            
            # Default handling for other file types
            return send_from_directory(UPLOAD_FOLDER, filename, 
                                     mimetype=mimetypes.guess_type(filename)[0],
                                     as_attachment=False)
        except Exception as e:
            logger.error(f"Error serving file {filename}: {str(e)}")
            abort(404)  # Not found
    
    # Add a route for media API (can be extended for more media operations)
    @app.route('/api/media/list')
    def list_media():
        """List all media files in the uploads directory"""
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            media_files = []
            
            # List all files in the uploads directory
            for file in os.listdir(UPLOAD_FOLDER):
                # Skip thumbnails and temporary files
                if file.endswith('_thumb.jpg') or file.startswith('.'):
                    continue
                
                file_path = os.path.join(UPLOAD_FOLDER, file)
                
                # Get file info
                file_stat = os.stat(file_path)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Determine file type
                file_type = 'unknown'
                if file_ext in ['.mp4', '.webm', '.mov', '.avi']:
                    file_type = 'video'
                elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    file_type = 'image'
                elif file_ext in ['.mp3', '.wav', '.ogg', '.aac']:
                    file_type = 'audio'
                
                # Add file info to list
                media_files.append({
                    'name': os.path.splitext(file)[0],
                    'path': f'/uploads/{file}',
                    'type': file_type,
                    'size': file_stat.st_size,
                    'created_at': file_stat.st_ctime,
                    'modified_at': file_stat.st_mtime
                })
            
            return jsonify({
                'success': True,
                'count': len(media_files),
                'media': media_files
            })
        except Exception as e:
            logger.error(f"Error listing media: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.info("Media routes added successfully")
    return True

if __name__ == "__main__":
    # This can be run as a standalone script to test routes
    app = Flask(__name__)
    add_media_routes(app)
    
    print("Media server routes added. This script is meant to be imported, not run directly.")