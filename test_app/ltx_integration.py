"""
LTX-Video Integration Module for OpenShot Web Editor

This module initializes and manages LTX-Video capabilities as part of the main application,
ensuring all AI features are available immediately when a user opens the video editor.
"""

import os
import sys
import threading
import time
import uuid
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ltx_integration")

# Global state
_ltx_initialized = False
_ltx_pipeline = None
_generation_jobs = {}
_model_paths = {
    "checkpoint": "/root/OpenShot/models/ltx-video/ltx-video-2b-v0.9.5.safetensors",
    "text_encoder": "PixArt-alpha/PixArt-XL-2-1024-MS",
}

def initialize_ltx():
    """Initialize LTX-Video capabilities during application startup"""
    global _ltx_initialized, _ltx_pipeline, _model_paths
    
    if _ltx_initialized:
        logger.info("LTX-Video already initialized")
        return True
    
    logger.info("Initializing LTX-Video integration...")
    
    # Ensure LTX-Video is in Python path
    ltx_path = Path("/root/OpenShot/LTX-Video")
    if ltx_path.exists() and str(ltx_path) not in sys.path:
        sys.path.append(str(ltx_path))
    
    # Check for model files and download if needed
    ensure_models_available()
    
    # Initialize in a separate thread to avoid blocking application startup
    threading.Thread(target=_initialize_ltx_background, daemon=True).start()
    
    return True

def _initialize_ltx_background():
    """Background initialization of LTX models to avoid blocking the main thread"""
    global _ltx_initialized, _ltx_pipeline, _model_paths
    
    try:
        logger.info("Loading LTX-Video models in background...")
        
        # Import LTX-Video components
        from inference import create_ltx_video_pipeline
        import torch
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {device}")
        
        # Load pipeline
        _ltx_pipeline = create_ltx_video_pipeline(
            ckpt_path=_model_paths["checkpoint"],
            precision="bfloat16" if device == "cuda" else "float32",
            text_encoder_model_name_or_path=_model_paths["text_encoder"],
            enhance_prompt=True,
            device=device
        )
        
        # Mark as initialized
        _ltx_initialized = True
        logger.info("LTX-Video initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize LTX-Video: {str(e)}")
        _ltx_initialized = False

def ensure_models_available():
    """Check if required model files are available and download if needed"""
    global _model_paths
    
    # Create model directory if it doesn't exist
    model_dir = Path("/root/OpenShot/models/ltx-video")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if model file exists
    model_file = model_dir / "ltx-video-2b-v0.9.5.safetensors"
    if not model_file.exists():
        logger.info("Model file not found, downloading...")
        download_model_files()
    else:
        logger.info(f"Model file found at {model_file}")
        
    # Update model path
    _model_paths["checkpoint"] = str(model_file)

def download_model_files():
    """Download required model files from Hugging Face"""
    try:
        logger.info("Downloading LTX-Video model files...")
        from huggingface_hub import hf_hub_download
        
        model_dir = "/root/OpenShot/models/ltx-video"
        
        # Download model weights
        hf_hub_download(
            repo_id="Lightricks/LTX-Video",
            filename="ltx-video-2b-v0.9.5.safetensors",
            local_dir=model_dir,
            local_dir_use_symlinks=False,
            repo_type='model'
        )
        
        logger.info("Model files downloaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to download model files: {str(e)}")
        raise

def generate_video(prompt, height=480, width=704, num_frames=121, 
                  seed=None, guidance_scale=3.0, output_dir=None):
    """
    Generate a video using LTX-Video
    
    Args:
        prompt: Text prompt describing the video
        height: Height of the video
        width: Width of the video
        num_frames: Number of frames to generate
        seed: Random seed for reproducibility
        guidance_scale: Guidance scale parameter
        output_dir: Directory to save the video (default: data/ai_generated)
        
    Returns:
        job_id: Unique identifier for the generation job
    """
    global _ltx_initialized, _ltx_pipeline, _generation_jobs
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Ensure output directory exists
    if output_dir is None:
        output_dir = os.path.join("/root/OpenShot/test_app/data/ai_generated")
    os.makedirs(output_dir, exist_ok=True)
    
    # Store job information
    _generation_jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'created_at': time.time(),
        'parameters': {
            'prompt': prompt,
            'height': height,
            'width': width,
            'num_frames': num_frames,
            'seed': seed,
            'guidance_scale': guidance_scale,
            'output_dir': output_dir
        }
    }
    
    # Start generation in a background thread
    threading.Thread(
        target=_run_generation_job, 
        args=(job_id,),
        daemon=True
    ).start()
    
    return job_id

def _run_generation_job(job_id):
    """Run a video generation job in the background"""
    global _ltx_initialized, _ltx_pipeline, _generation_jobs
    
    # Get job parameters
    job = _generation_jobs[job_id]
    params = job['parameters']
    
    try:
        # Wait for LTX initialization if needed
        start_time = time.time()
        while not _ltx_initialized and time.time() - start_time < 60:
            time.sleep(1)
            
        if not _ltx_initialized:
            raise Exception("LTX-Video initialization timeout")
            
        # Update job status
        _generation_jobs[job_id]['status'] = 'processing'
        
        # Import required modules
        import torch
        from pathlib import Path
        
        # Setup generation parameters
        timestamp = int(time.time())
        safe_prompt = ''.join(c if c.isalnum() or c.isspace() else '_' for c in params['prompt'][:20]).strip()
        safe_prompt = safe_prompt.replace(' ', '_')
        
        result_filename = f"ai_generated_{safe_prompt}_{timestamp}.mp4"
        output_path = os.path.join(params['output_dir'], result_filename)
        
        # Set seed
        seed = params['seed'] if params['seed'] is not None else int(time.time()) % 1000000
        generator = torch.Generator("cuda" if torch.cuda.is_available() else "cpu").manual_seed(seed)
        
        # Directly use the pipeline for generation
        # This skips some features of the full inference.py script but is more straightforward to integrate
        from ltx_video.utils.skip_layer_strategy import SkipLayerStrategy
        
        # Update job progress
        _generation_jobs[job_id]['progress'] = 10
        
        # Setup basic parameters
        stg_mode = "attention_values"
        skip_block_list = [int(x.strip()) for x in "19".split(",")]
        
        if stg_mode.lower() == "stg_av" or stg_mode.lower() == "attention_values":
            skip_layer_strategy = SkipLayerStrategy.AttentionValues
        elif stg_mode.lower() == "stg_as" or stg_mode.lower() == "attention_skip":
            skip_layer_strategy = SkipLayerStrategy.AttentionSkip
        elif stg_mode.lower() == "stg_r" or stg_mode.lower() == "residual":
            skip_layer_strategy = SkipLayerStrategy.Residual
        elif stg_mode.lower() == "stg_t" or stg_mode.lower() == "transformer_block":
            skip_layer_strategy = SkipLayerStrategy.TransformerBlock
        else:
            raise ValueError(f"Invalid spatiotemporal guidance mode: {stg_mode}")
        
        # Update job progress
        _generation_jobs[job_id]['progress'] = 20
        
        # Make width and height divisible by 32
        height_padded = ((params['height'] - 1) // 32 + 1) * 32
        width_padded = ((params['width'] - 1) // 32 + 1) * 32
        
        # Make num_frames (N * 8 + 1)
        num_frames_padded = ((params['num_frames'] - 2) // 8 + 1) * 8 + 1
        
        # Run generation
        images = _ltx_pipeline(
            prompt=params['prompt'],
            negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted",
            num_inference_steps=40,
            guidance_scale=params['guidance_scale'],
            skip_layer_strategy=skip_layer_strategy,
            skip_block_list=skip_block_list,
            stg_scale=1.0,
            do_rescaling=True,
            rescaling_scale=0.7,
            generator=generator,
            output_type="pt",
            height=height_padded,
            width=width_padded,
            num_frames=num_frames_padded,
            frame_rate=25,
            is_video=True,
            vae_per_channel_normalize=True,
            image_cond_noise_scale=0.15,
            decode_timestep=0.025,
            decode_noise_scale=0.0125,
            mixed_precision=True,
            offload_to_cpu=False,
            enhance_prompt=True,
        ).images
        
        # Update job progress
        _generation_jobs[job_id]['progress'] = 80
        
        # Save to file
        import imageio
        
        # Convert tensor to numpy array
        video_np = images[0].permute(1, 2, 3, 0).cpu().float().numpy()
        
        # Unnormalize to [0, 255] range
        video_np = (video_np * 255).astype('uint8')
        
        # Crop to original requested dimensions
        video_np = video_np[:params['num_frames'], :params['height'], :params['width'], :]
        
        # Write video file
        with imageio.get_writer(output_path, fps=25) as video:
            for frame in video_np:
                video.append_data(frame)
        
        # Update job status with success
        _generation_jobs[job_id].update({
            'status': 'completed',
            'result_path': output_path,
            'completed_at': time.time(),
            'progress': 100
        })
        
        logger.info(f"Video generation completed: {output_path}")
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        
        # Update job status with error
        _generation_jobs[job_id].update({
            'status': 'failed',
            'error': str(e),
            'completed_at': time.time()
        })

def get_job_status(job_id):
    """Get the status of a generation job"""
    global _generation_jobs
    
    if job_id not in _generation_jobs:
        return {'error': 'Job not found', 'status': 'not_found'}
    
    return _generation_jobs[job_id]

def is_initialized():
    """Check if LTX-Video is initialized and ready"""
    global _ltx_initialized
    return _ltx_initialized

# Additional utility functions for the Flask routes

def get_ltx_status():
    """Get the current LTX system status for diagnostics"""
    global _ltx_initialized, _ltx_pipeline
    
    import torch
    
    status = {
        'initialized': _ltx_initialized,
        'gpu_available': torch.cuda.is_available(),
        'model_loaded': _ltx_pipeline is not None,
        'active_jobs': sum(1 for job in _generation_jobs.values() if job['status'] == 'processing'),
        'queued_jobs': sum(1 for job in _generation_jobs.values() if job['status'] == 'queued'),
        'completed_jobs': sum(1 for job in _generation_jobs.values() if job['status'] == 'completed'),
        'failed_jobs': sum(1 for job in _generation_jobs.values() if job['status'] == 'failed')
    }
    
    if torch.cuda.is_available():
        status.update({
            'gpu_name': torch.cuda.get_device_name(0),
            'gpu_memory_allocated': f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB",
            'gpu_memory_reserved': f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB",
        })
    
    return status

# Initialize on module import
initialize_ltx()