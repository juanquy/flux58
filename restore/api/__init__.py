#!/usr/bin/env python3
"""
FLUX58 AI MEDIA LABS - API Routes
API endpoints for the FLUX58 video editing web application
"""

import os
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, session

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Check if we can import OpenShot
try:
    import openshot
    from openshot_api import openshot_api
    OPENSHOT_AVAILABLE = True
except ImportError:
    OPENSHOT_AVAILABLE = False

@api_bp.route('/openshot/status')
def openshot_status():
    """API endpoint to check OpenShot library status"""
    try:
        from openshot_api import openshot_api
        status = openshot_api.get_status()
        return jsonify(status)
    except Exception as e:
        print(f"Error getting OpenShot status: {str(e)}")
        return jsonify({
            "available": False,
            "version": "Unknown",
            "message": f"OpenShot library not available: {str(e)}",
            "capabilities": {
                "video_editing": False,
                "audio_editing": False,
                "rendering": False,
                "effects": False
            }
        })

def init_api_routes(app, db, project_manager, export_queue):
    """Register API routes with the app"""
    app.register_blueprint(api_bp, url_prefix='/api')
