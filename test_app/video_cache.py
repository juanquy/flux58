import redis
import os
import json
import hashlib
from datetime import datetime, timedelta
import torch
import cv2
import numpy as np

class VideoCache:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.cache_expiry = timedelta(days=7)  # Cache expires after 7 days
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def _generate_cache_key(self, video_path, operation, params=None):
        """Generate a unique cache key for the operation"""
        key_parts = [video_path, operation]
        if params:
            key_parts.append(json.dumps(params, sort_keys=True))
        return hashlib.md5(''.join(key_parts).encode()).hexdigest()

    def _get_video_metadata(self, video_path):
        """Get video metadata for cache invalidation"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        metadata = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'last_modified': os.path.getmtime(video_path)
        }
        cap.release()
        return metadata

    def get_cached_result(self, video_path, operation, params=None):
        """Get cached result if available"""
        cache_key = self._generate_cache_key(video_path, operation, params)
        
        # Check if cache exists
        if not self.redis.exists(cache_key):
            return None
        
        # Get cache metadata
        metadata = self.redis.hgetall(f"{cache_key}:metadata")
        if not metadata:
            return None
        
        # Check if video has been modified
        current_metadata = self._get_video_metadata(video_path)
        if not current_metadata:
            return None
        
        # Invalidate cache if video has changed
        if (current_metadata['last_modified'] > float(metadata['last_modified']) or
            current_metadata['frame_count'] != int(metadata['frame_count'])):
            self.invalidate_cache(cache_key)
            return None
        
        # Return cached result
        result_path = self.redis.get(cache_key)
        if result_path and os.path.exists(result_path):
            return result_path
        return None

    def cache_result(self, video_path, operation, result_path, params=None):
        """Cache the result of an operation"""
        cache_key = self._generate_cache_key(video_path, operation, params)
        metadata = self._get_video_metadata(video_path)
        
        if metadata:
            # Store metadata
            self.redis.hmset(f"{cache_key}:metadata", metadata)
            self.redis.expire(f"{cache_key}:metadata", self.cache_expiry)
            
            # Store result path
            self.redis.set(cache_key, result_path)
            self.redis.expire(cache_key, self.cache_expiry)

    def invalidate_cache(self, cache_key):
        """Invalidate cache for a specific key"""
        self.redis.delete(cache_key)
        self.redis.delete(f"{cache_key}:metadata")

    def clear_all_cache(self):
        """Clear all video processing cache"""
        for key in self.redis.keys("*:metadata"):
            self.redis.delete(key)
            self.redis.delete(key[:-9])  # Remove :metadata suffix

class GPUAccelerator:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.cache = VideoCache()

    def process_video(self, video_path, operation, params=None):
        """Process video with GPU acceleration if available"""
        # Check cache first
        cached_result = self.cache.get_cached_result(video_path, operation, params)
        if cached_result:
            return cached_result

        # Process video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Create output video writer
        output_path = f"processed_{os.path.basename(video_path)}"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Process frames
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert frame to tensor and move to GPU
            frame_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
            frame_tensor = frame_tensor.to(self.device)

            # Apply processing (example: simple enhancement)
            if operation == 'enhance':
                # Example enhancement operation
                enhanced = self._enhance_frame(frame_tensor)
            else:
                enhanced = frame_tensor

            # Convert back to numpy and write to output
            enhanced_np = (enhanced.permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
            out.write(enhanced_np)

            frame_count += 1
            if frame_count % 10 == 0:
                print(f"Processed {frame_count}/{total_frames} frames")

        cap.release()
        out.release()

        # Cache the result
        self.cache.cache_result(video_path, operation, output_path, params)
        return output_path

    def _enhance_frame(self, frame_tensor):
        """Example frame enhancement using GPU"""
        # Simple enhancement example
        enhanced = frame_tensor * 1.2  # Increase brightness
        enhanced = torch.clamp(enhanced, 0, 1)  # Clamp values
        return enhanced 