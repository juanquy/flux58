# OpenShot AI Integration Documentation

## LTX-Video Integration

The OpenShot editor now features AI-powered text-to-video generation capabilities through integration with LTX-Video. This document provides an overview of the implementation, usage instructions, and future development plans.

### Architecture Overview

The integration consists of these key components:

1. **Core Integration Module** (`ltx_integration.py`)
   - Provides direct integration with LTX-Video library
   - Handles model initialization and video generation
   - Manages generation jobs and their status
   - Implements background processing to avoid blocking the UI

2. **API Layer** (`ltx_routes.py`)
   - Provides Flask routes for the web application
   - Handles authentication and credit tracking
   - Manages file storage and project integration
   - Implements error handling and status reporting

3. **Client-Side Integration** (`ltx_video.js`)
   - Connects the UI to the API endpoints
   - Provides status monitoring and progress display
   - Handles video importing into projects
   - Implements advanced generation options

### User Guide

#### Basic Video Generation
1. Open any project in the editor
2. Find the AI Tools section in the media panel
3. Enter a text prompt describing your desired video
4. Click the lightning icon to start generation
5. Monitor progress in the media panel
6. Click the completed item to import it into your project

#### Advanced Video Generation
1. Click the "AI Assist" button in the editor header
2. Enter a detailed text prompt
3. Adjust video dimensions and duration using the provided controls
4. Click "Generate Video" to start the process
5. Monitor progress in the media panel
6. Click the completed item to import it into your project

#### Tips for Better Results
- Use detailed, descriptive prompts
- Specify camera angles and movements
- Include specific details about lighting and style
- Keep videos short (3-10 seconds) for best quality
- Experiment with different guidance scale values

### Technical Documentation

#### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ltx/status` | GET | Get LTX service status |
| `/api/ltx/generate` | POST | Generate video from text |
| `/api/ltx/status/<job_id>` | GET | Check job status |
| `/api/ltx/import/<job_id>` | POST | Import video to project |

#### Generate Video Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | string | Text description of desired video |
| `height` | integer | Video height in pixels |
| `width` | integer | Video width in pixels |
| `num_frames` | integer | Total frames to generate |
| `seed` | integer | Random seed for reproducibility |
| `guidance_scale` | float | Controls adherence to prompt |

#### Credit Usage

Each text-to-video generation costs 15 credits, as specified in the AI_FEATURES.md document. Credits are deducted when generation starts, regardless of completion status.

#### File Storage

Generated videos are stored in:
- Temporary: `/root/OpenShot/test_app/data/ai_generated/{user_id}/`
- After import: `/root/OpenShot/test_app/data/uploads/project_{project_id}/`

### Next Development Steps

The next logical steps for enhancing the AI integration are:

1. **Image-to-Video Implementation**
   - Allow users to upload images and animate them
   - Add controls for animation style and movement
   - Implement zooming, panning, and perspective animations
   - Connect to the existing UI placeholders in the editor

2. **Style Control Enhancements**
   - Add style presets for different video aesthetics
   - Implement fine-grained control over video style
   - Add reference image upload for style matching
   - Create a library of style samples

3. **Video Extension Capability**
   - Allow extending existing videos with AI
   - Implement seamless continuation of generated videos
   - Add scene variation options for the same prompt
   - Build shot sequencing from multiple generations

4. **Performance Optimizations**
   - Implement better model caching
   - Add progressive generation quality levels
   - Optimize memory usage for larger videos
   - Implement batch processing for multiple jobs

5. **UI/UX Improvements**
   - Add real-time preview during generation
   - Implement better error visualization
   - Add thumbnail preview before importing
   - Create a gallery of recent generations

These enhancements will significantly improve the AI capabilities of the OpenShot editor, making it a more powerful tool for video creation with artificial intelligence.

### Troubleshooting

**Generation Fails to Start**
- Check if LTX service is initialized (may take 1-2 minutes after startup)
- Verify sufficient credits in account
- Ensure prompt is not empty

**Low Quality Results**
- Use more detailed prompts
- Try adjusting the guidance scale
- Reduce video dimensions for better quality
- Keep videos short (5 seconds or less for best quality)

**Import Errors**
- Check disk space in project directory
- Ensure the generation completed successfully
- Verify the project is still open

### Conclusion

The LTX-Video integration represents the first step in adding comprehensive AI capabilities to the OpenShot editor. Future updates will expand on this foundation to create a powerful AI-assisted video creation platform.