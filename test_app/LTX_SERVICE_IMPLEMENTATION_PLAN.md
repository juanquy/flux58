# LTX-Video Service Implementation Plan

## Overview

This document outlines the steps to implement the LTX-Video text-to-video generation service for integration with the OpenShot video editor. The service will run locally on the server and provide an API for generating videos from text prompts.

## Prerequisites

Based on analysis of the LTX-Video repository, the following prerequisites are needed:

1. **Python 3.10+** (tested with Python 3.10.5)
2. **CUDA 12.2** for GPU acceleration (or MPS on MacOS)
3. **PyTorch 2.1.2+** (2.3.0+ for MacOS MPS support)
4. **Model checkpoint** from Hugging Face (ltx-video-2b-v0.9.5.safetensors)
5. **Text encoder models** from Hugging Face (PixArt-alpha/PixArt-XL-2-1024-MS)
6. **Dependencies**:
   - diffusers >= 0.28.2
   - transformers >= 4.47.2
   - sentencepiece >= 0.1.96
   - huggingface-hub ~= 0.25.2
   - einops
   - timm
   - accelerate
   - matplotlib
   - imageio[ffmpeg]

## Implementation Steps

### 1. Set up Virtual Environment

```bash
python3 -m venv /root/OpenShot/ltx_video_env
source /root/OpenShot/ltx_video_env/bin/activate
pip install -e /root/OpenShot/LTX-Video[inference-script]
```

### 2. Download Model Checkpoint

```python
from huggingface_hub import hf_hub_download

model_dir = '/root/OpenShot/models/ltx-video'
hf_hub_download(
    repo_id="Lightricks/LTX-Video", 
    filename="ltx-video-2b-v0.9.5.safetensors", 
    local_dir=model_dir, 
    local_dir_use_symlinks=False, 
    repo_type='model'
)
```

### 3. Create Flask API Service

Create a Python Flask service that exposes the LTX-Video generation capabilities via a REST API:

```python
from flask import Flask, request, jsonify
import threading
import time
import uuid
import os

app = Flask(__name__)

# Store job status
jobs = {}

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """API endpoint to start a video generation job"""
    data = request.json
    
    # Create a unique job ID
    job_id = str(uuid.uuid4())
    
    # Store job information
    jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'created_at': time.time(),
        'parameters': data
    }
    
    # Start generation in a background thread
    threading.Thread(target=process_generation_job, args=(job_id, data)).start()
    
    return jsonify({'job_id': job_id, 'status': 'queued'})

@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Check the status of a generation job"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
        
    return jsonify(jobs[job_id])

@app.route('/api/result/<job_id>', methods=['GET'])
def get_job_result(job_id):
    """Get the result of a completed job"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    if jobs[job_id]['status'] != 'completed':
        return jsonify({'error': 'Job not yet completed'}), 400
        
    # Return the file path or stream the file
    return jsonify({
        'status': 'completed',
        'result_path': jobs[job_id].get('result_path')
    })

def process_generation_job(job_id, parameters):
    """Background process to handle the video generation"""
    try:
        # Update job status
        jobs[job_id]['status'] = 'processing'
        
        # Extract parameters for generation
        prompt = parameters.get('prompt', '')
        height = parameters.get('height', 480)
        width = parameters.get('width', 704)
        num_frames = parameters.get('num_frames', 121)
        seed = parameters.get('seed', int(time.time()) % 1000000)
        guidance_scale = parameters.get('guidance_scale', 3.0)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join('/root/OpenShot/test_app/data/ai_generated')
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output path
        timestamp = int(time.time())
        filename_base = f"generated_{timestamp}"
        output_path = os.path.join(output_dir, filename_base)
        
        # Use the inference.py script to generate the video
        # This will be replaced with direct API calls to the LTX-Video module
        from inference import infer
        
        # Setup additional parameters
        inference_params = {
            'ckpt_path': '/root/OpenShot/models/ltx-video',
            'output_path': output_dir,
            'height': height,
            'width': width,
            'num_frames': num_frames,
            'seed': seed,
            'prompt': prompt,
            'guidance_scale': guidance_scale,
            'num_inference_steps': 40,
            'stg_scale': 1.0,
            'stg_rescale': 0.7,
            'stg_mode': 'attention_values',
            'stg_skip_layers': '19',
            'frame_rate': 25,
            'text_encoder_model_name_or_path': 'PixArt-alpha/PixArt-XL-2-1024-MS',
            'negative_prompt': 'worst quality, inconsistent motion, blurry, jittery, distorted'
        }
        
        # Run inference (this will be modified to provide progress updates)
        infer(**inference_params)
        
        # Find the generated video file
        generated_files = [f for f in os.listdir(output_dir) 
                         if f.startswith(f"video_output_0_{prompt.split()[0]}")
                         and f.endswith('.mp4')]
        
        if generated_files:
            result_path = os.path.join(output_dir, generated_files[0])
            
            # Update job status with success
            jobs[job_id].update({
                'status': 'completed',
                'result_path': result_path,
                'completed_at': time.time()
            })
        else:
            # Update job status with failure
            jobs[job_id].update({
                'status': 'failed',
                'error': 'No output file found',
                'completed_at': time.time()
            })
            
    except Exception as e:
        # Update job status with error
        jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'completed_at': time.time()
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5095)
```

### 4. Create Installation and Setup Script

Create a Bash script to automate the installation and setup of the LTX-Video service:

```bash
#!/bin/bash
# setup_ltx_service.sh

set -e

# Create directories
mkdir -p /root/OpenShot/models/ltx-video
mkdir -p /root/OpenShot/test_app/data/ai_generated

# Create and activate virtual environment
python3 -m venv /root/OpenShot/ltx_video_env
source /root/OpenShot/ltx_video_env/bin/activate

# Install LTX-Video and dependencies
pip install -e /root/OpenShot/LTX-Video[inference-script]

# Download model checkpoint
python3 -c "
from huggingface_hub import hf_hub_download
import os

model_dir = '/root/OpenShot/models/ltx-video'
os.makedirs(model_dir, exist_ok=True)

# Download the model weights
hf_hub_download(
    repo_id='Lightricks/LTX-Video',
    filename='ltx-video-2b-v0.9.5.safetensors',
    local_dir=model_dir,
    local_dir_use_symlinks=False,
    repo_type='model'
)
"

# Copy service files
cp /root/OpenShot/test_app/ltx_video_service.py /root/OpenShot/

# Create systemd service file
cat > /etc/systemd/system/ltx-video-service.service << EOF
[Unit]
Description=LTX Video Generation Service
After=network.target

[Service]
User=root
WorkingDirectory=/root/OpenShot
ExecStart=/root/OpenShot/ltx_video_env/bin/python /root/OpenShot/ltx_video_service.py
Restart=on-failure
RestartSec=5s
Environment=PYTHONPATH=/root/OpenShot/LTX-Video

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
systemctl daemon-reload
systemctl enable ltx-video-service
systemctl start ltx-video-service

echo "LTX Video Service installed and started!"
```

### 5. Create Integration with OpenShot

Create a Python module in the OpenShot test_app to interact with the LTX-Video service:

```python
# /root/OpenShot/test_app/ltx_api.py

import requests
import time
import os

class LTXVideoClient:
    """Client for the LTX-Video generation service"""
    
    def __init__(self, base_url="http://localhost:5095/api"):
        self.base_url = base_url
        
    def generate_video(self, prompt, height=480, width=704, num_frames=121, 
                       seed=None, guidance_scale=3.0, wait=False, timeout=600):
        """
        Generate a video using the LTX-Video service
        
        Args:
            prompt: Text prompt describing the video
            height: Height of the video (default: 480)
            width: Width of the video (default: 704)
            num_frames: Number of frames to generate (default: 121)
            seed: Random seed for reproducibility (default: None)
            guidance_scale: Guidance scale (default: 3.0)
            wait: Whether to wait for the job to complete (default: False)
            timeout: Maximum time to wait in seconds (default: 10 minutes)
            
        Returns:
            dict: Job information including job_id and status
        """
        params = {
            'prompt': prompt,
            'height': height,
            'width': width,
            'num_frames': num_frames,
            'seed': seed,
            'guidance_scale': guidance_scale
        }
        
        # Start the generation job
        response = requests.post(f"{self.base_url}/generate", json=params)
        response.raise_for_status()
        
        job_data = response.json()
        job_id = job_data['job_id']
        
        if not wait:
            return job_data
            
        # Wait for the job to complete
        start_time = time.time()
        while True:
            job_data = self.get_job_status(job_id)
            
            if job_data['status'] == 'completed':
                # Get the result path
                result = self.get_job_result(job_id)
                job_data['result_path'] = result.get('result_path')
                return job_data
                
            if job_data['status'] == 'failed':
                return job_data
                
            # Check timeout
            if time.time() - start_time > timeout:
                job_data['status'] = 'timeout'
                return job_data
                
            # Wait before checking again
            time.sleep(5)
    
    def get_job_status(self, job_id):
        """Get the status of a generation job"""
        response = requests.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()
        
    def get_job_result(self, job_id):
        """Get the result of a completed job"""
        response = requests.get(f"{self.base_url}/result/{job_id}")
        response.raise_for_status()
        return response.json()
```

### 6. Create Web UI Integration

Add routes to the OpenShot Flask app to allow users to generate videos from the UI:

```python
# Add these routes to app.py

@app.route('/ai/generate', methods=['POST'])
@login_required
def ai_generate_video():
    """Generate a video using AI"""
    data = request.json
    prompt = data.get('prompt', '')
    height = int(data.get('height', 480))
    width = int(data.get('width', 704))
    
    # Initialize LTX client
    from ltx_api import LTXVideoClient
    client = LTXVideoClient()
    
    # Start generation job
    job = client.generate_video(
        prompt=prompt,
        height=height,
        width=width,
        wait=False
    )
    
    return jsonify(job)

@app.route('/ai/status/<job_id>', methods=['GET'])
@login_required
def ai_job_status(job_id):
    """Check the status of an AI generation job"""
    from ltx_api import LTXVideoClient
    client = LTXVideoClient()
    
    status = client.get_job_status(job_id)
    return jsonify(status)

@app.route('/ai/import/<job_id>', methods=['POST'])
@login_required
def ai_import_video(job_id):
    """Import a generated video into the current project"""
    data = request.json
    project_id = data.get('project_id')
    
    # Get the job details
    from ltx_api import LTXVideoClient
    client = LTXVideoClient()
    
    result = client.get_job_result(job_id)
    
    if result.get('status') != 'completed':
        return jsonify({'error': 'Video generation not completed'}), 400
        
    source_path = result.get('result_path')
    if not source_path or not os.path.exists(source_path):
        return jsonify({'error': 'Generated video file not found'}), 404
        
    # Import video into project
    from projects import ProjectManager
    pm = ProjectManager()
    
    # Copy file to project directory
    filename = os.path.basename(source_path)
    dest_path = os.path.join(
        app.config['UPLOAD_FOLDER'], 
        f'project_{project_id}', 
        f'ai_generated_{filename}'
    )
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy(source_path, dest_path)
    
    # Add asset to project
    asset_id = pm.add_asset(
        project_id=project_id,
        user_id=current_user.id,
        name=f"AI Generated: {data.get('prompt', '')[:30]}",
        asset_type="video",
        file_path=dest_path
    )
    
    return jsonify({
        'asset_id': asset_id,
        'file_path': dest_path
    })
```

## Next Steps

Based on our examination of the LTX-Video codebase and requirements, these are the immediate next steps for implementation:

1. **Create Model Download Script**: Create a script to download the required models from Hugging Face
2. **Build Flask API Service**: Implement the Flask API service for video generation
3. **Test Generation Parameters**: Test various generation parameters to find optimal settings
4. **Set Up Service Management**: Configure systemd service for automatic startup
5. **Integrate with UI**: Implement UI integration in the OpenShot web app
6. **Implement Job Queue**: Add job queue for managing multiple generation requests
7. **Add Progress Tracking**: Implement progress tracking for long-running generation jobs

## Resource Requirements

- **Disk Space**: ~5GB for model files
- **RAM**: Minimum 16GB, recommended 32GB
- **GPU**: CUDA-capable NVIDIA GPU with 8GB+ VRAM (16GB+ recommended)
- **CPU**: Modern multi-core CPU if running without GPU acceleration

The initial implementation will focus on running the service locally on the server. Future iterations could explore containerization with Docker for easier deployment and isolation.