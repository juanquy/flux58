from flask import Blueprint, jsonify, request, current_app
from gradio_interface import GradioInterface
from video_cache import GPUAccelerator
import threading
import os
import json

# Create Blueprint for AI features
ai_bp = Blueprint('ai', __name__)

# Initialize components
gradio_interface = None
gpu_accelerator = None

def init_ai_components(app):
    """Initialize AI components"""
    global gradio_interface, gpu_accelerator
    
    # Initialize Gradio interface
    gradio_interface = GradioInterface()
    
    # Initialize GPU accelerator
    gpu_accelerator = GPUAccelerator()
    
    # Start Gradio interface in background thread
    def start_gradio():
        gradio_app = gradio_interface.create_ai_interface()
        gradio_app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    
    gradio_thread = threading.Thread(target=start_gradio, daemon=True)
    gradio_thread.start()

@ai_bp.route('/ai-tools')
def ai_tools():
    """Redirect to Gradio interface"""
    return jsonify({
        'status': 'success',
        'url': 'http://localhost:7860'
    })

@ai_bp.route('/process-video', methods=['POST'])
def process_video():
    """Process video with GPU acceleration"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    operation = request.form.get('operation', 'enhance')
    params = request.form.get('params', None)
    
    if params:
        try:
            params = json.loads(params)
        except json.JSONDecodeError:
            params = None
    
    # Save uploaded file
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    video_path = os.path.join(upload_folder, video_file.filename)
    video_file.save(video_path)
    
    try:
        # Process video with GPU acceleration
        result_path = gpu_accelerator.process_video(
            video_path,
            operation,
            params
        )
        
        return jsonify({
            'status': 'success',
            'result_path': result_path
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@ai_bp.route('/style-transfer', methods=['POST'])
def style_transfer():
    """Apply style transfer to video"""
    if 'video' not in request.files or 'style' not in request.files:
        return jsonify({'error': 'Missing video or style image'}), 400
    
    video_file = request.files['video']
    style_file = request.files['style']
    strength = float(request.form.get('strength', 0.5))
    
    # Save uploaded files
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    video_path = os.path.join(upload_folder, video_file.filename)
    style_path = os.path.join(upload_folder, style_file.filename)
    
    video_file.save(video_path)
    style_file.save(style_path)
    
    try:
        # Process with Gradio interface
        result = gradio_interface._style_transfer(video_path, style_path, strength)
        return jsonify({
            'status': 'success',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@ai_bp.route('/generate-video', methods=['POST'])
def generate_video():
    """Generate video from text"""
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'error': 'Missing prompt'}), 400
    
    prompt = data['prompt']
    duration = int(data.get('duration', 5))
    
    try:
        # Generate with Gradio interface
        result = gradio_interface._generate_video(prompt, duration)
        return jsonify({
            'status': 'success',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def register_ai_routes(app):
    """Register AI routes with the Flask app"""
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    init_ai_components(app) 