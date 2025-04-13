"""
LTX-Video AI Routes for OpenShot Web Editor

This module provides Flask routes for the LTX-Video integration with the OpenShot web editor.
These routes allow users to generate videos from text prompts, check generation status,
and import generated videos into their projects.
"""

from flask import Blueprint, jsonify, request, session, current_app
from functools import wraps
import os
import shutil
import uuid
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ltx_routes")

# Import LTX integration
from ltx_integration import (
    generate_video,
    get_job_status,
    get_ltx_status,
    is_initialized
)

# Import database module for credit tracking
import database as db

# Create blueprint
ltx_bp = Blueprint('ltx', __name__, url_prefix='/api/ltx')

# Decorator for requiring login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes for LTX-Video integration

@ltx_bp.route('/status', methods=['GET'])
@login_required
def ltx_status():
    """Get current status of LTX-Video service"""
    status = get_ltx_status()
    return jsonify(status)

@ltx_bp.route('/generate', methods=['POST'])
@login_required
def ltx_generate():
    """Generate a video using LTX-Video"""
    user_id = session.get('user_id')
    data = request.json
    
    # Validate input
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Prompt is required'}), 400
    
    # Get parameters
    prompt = data.get('prompt', '')
    height = int(data.get('height', 480))
    width = int(data.get('width', 704))
    num_frames = int(data.get('num_frames', 121))
    seed = data.get('seed')
    guidance_scale = float(data.get('guidance_scale', 3.0))
    
    # Check if LTX is initialized
    if not is_initialized() and time.time() % 2 == 0:  # Allow 50% of requests through during initialization
        # If not yet initialized, allow the request but inform the user
        status = get_ltx_status()
        logger.info(f"LTX not yet initialized, status: {status}")
    
    # Check user credits
    user_credits = db.get_user_credits(user_id) or {"total": 0, "used": 0}
    available_credits = user_credits.get("total", 0) - user_credits.get("used", 0)
    
    required_credits = 15  # Text2Video costs 15 credits as defined in AI_FEATURES.md
    
    if available_credits < required_credits:
        return jsonify({
            'error': 'Not enough credits',
            'available': available_credits,
            'required': required_credits
        }), 402
    
    # Generate video in background
    output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f'ai_generated_{user_id}')
    os.makedirs(output_dir, exist_ok=True)
    
    job_id = generate_video(
        prompt=prompt,
        height=height,
        width=width,
        num_frames=num_frames,
        seed=seed,
        guidance_scale=guidance_scale,
        output_dir=output_dir
    )
    
    # Use credits
    description = f"AI Text2Video: {prompt[:30]}..." if len(prompt) > 30 else f"AI Text2Video: {prompt}"
    db.use_credits(user_id, required_credits, description, "ai_generation")
    
    # Return job information
    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'credits_used': required_credits
    })

@ltx_bp.route('/status/<job_id>', methods=['GET'])
@login_required
def ltx_job_status(job_id):
    """Check the status of a video generation job"""
    status = get_job_status(job_id)
    return jsonify(status)

@ltx_bp.route('/import/<job_id>', methods=['POST'])
@login_required
def ltx_import_video(job_id):
    """Import a generated video into a project"""
    user_id = session.get('user_id')
    data = request.json
    
    # Validate input
    if not data or 'project_id' not in data:
        return jsonify({'error': 'Project ID is required'}), 400
    
    project_id = data.get('project_id')
    
    # Get job status
    job = get_job_status(job_id)
    
    if job.get('status') != 'completed':
        return jsonify({'error': 'Video generation not completed', 'job_status': job}), 400
    
    # Get the source path
    source_path = job.get('result_path')
    if not source_path or not os.path.exists(source_path):
        return jsonify({'error': 'Generated video file not found'}), 404
    
    # Create destination path
    output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f'project_{project_id}')
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy to project directory
    filename = os.path.basename(source_path)
    dest_path = os.path.join(output_dir, f'ai_generated_{filename}')
    
    try:
        shutil.copy(source_path, dest_path)
    except Exception as e:
        logger.error(f"Error copying file: {str(e)}")
        return jsonify({'error': f'Error copying file: {str(e)}'}), 500
    
    # Import as project asset
    try:
        from projects import ProjectManager
        pm = ProjectManager()
        
        asset_id = pm.add_asset(
            project_id=project_id,
            user_id=user_id,
            name=f"AI Generated: {job['parameters']['prompt'][:30]}",
            asset_type="video",
            file_path=dest_path,
            info={
                "duration": job.get('parameters', {}).get('num_frames', 121) / 25.0,  # Assuming 25 fps
                "width": job.get('parameters', {}).get('width', 704),
                "height": job.get('parameters', {}).get('height', 480),
                "source": "ai_generated",
                "prompt": job.get('parameters', {}).get('prompt', '')
            }
        )
        
        return jsonify({
            'success': True,
            'asset_id': asset_id,
            'file_path': dest_path,
            'name': f"AI Generated: {job['parameters']['prompt'][:30]}"
        })
        
    except Exception as e:
        logger.error(f"Error adding asset to project: {str(e)}")
        return jsonify({'error': f'Error adding asset to project: {str(e)}'}), 500