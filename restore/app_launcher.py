#!/usr/bin/env python3
"""
FLUX58 AI MEDIA LABS - Web Application Launcher
A unified launcher for the FLUX58 video editing web application
"""

import os
import sys
import secrets
import logging
from datetime import timedelta
from flask import Flask, session, request
from werkzeug.middleware.proxy_fix import ProxyFix

# Import the consolidated application
from flux58_app import (
    Database, ProjectManager, init_logger, 
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS,
    FLASK_SECRET_KEY, BASE_DIR, LOGS_DIR
)

# Setup logging
logger = init_logger(log_dir=LOGS_DIR, log_level=logging.INFO)

# Create Flask application
app = Flask(__name__)

# Fix for running behind proxies
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Configure Flask
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'data', 'uploads')
app.config['PROPAGATE_EXCEPTIONS'] = True

# Initialize database
db = Database(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)

# Initialize project manager
project_manager = ProjectManager(db)

# Make sessions permanent by default
@app.before_request
def make_session_permanent():
    session.permanent = True

# Update session activity
@app.before_request
def update_session_activity():
    if 'user_id' in session and 'session_token' in session:
        try:
            # Update session activity in database
            db.update_session_activity(session['session_token'], request.remote_addr)
        except Exception as e:
            app.logger.error(f"Error updating session activity: {str(e)}")

# Clean up expired sessions periodically
@app.before_request
def cleanup_expired_sessions():
    # Only run occasionally (1 in 100 requests)
    if secrets.randbelow(100) == 0:
        try:
            count = db.cleanup_expired_sessions()
            if count > 0:
                app.logger.info(f"Cleaned up {count} expired sessions")
        except Exception as e:
            app.logger.error(f"Error cleaning up sessions: {str(e)}")

# Import routes - this must be after database and project_manager initialization
from routes import register_routes
register_routes(app, db, project_manager)

if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)