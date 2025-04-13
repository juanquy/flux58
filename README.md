# Flux58 

A video editing web application built on top of OpenShot with enhanced media management, editor UI, and AI video generation capabilities.

## Features

- Web-based video editor interface
- Project management system
- Media library with thumbnails
- User authentication and credits system
- Admin dashboard
- AI-powered video features:
  - Style transfer for videos
  - Video enhancement with GPU acceleration
  - Text-to-video generation
  - Real-time video processing
- PostgreSQL database integration
- Redis caching for improved performance

## Setup and Installation

Please refer to the documentation:
- [CLAUDE.md](CLAUDE.md) - Main documentation and operation instructions
- [PORTABLE.md](PORTABLE.md) - Guidelines for portable deployment
- [EDITOR_UI_IMPROVEMENTS.md](EDITOR_UI_IMPROVEMENTS.md) - Editor UI features and enhancements

### Dependencies

```bash
# Install Redis for caching
sudo apt-get install redis-server

# Install Python dependencies
pip install -r test_app/requirements.txt
```

## Running the Application

```bash
# Using the enhanced automated launcher script (recommended)
./run_flux58.sh

# Optional: Specify a custom port
PORT=5091 ./run_flux58.sh
```

### AI Features

Access the AI tools through:
- Web Interface: `http://your-server/ai-tools`
- Advanced Gradio Interface: `http://your-server:7860`

Available AI features:
1. Style Transfer
   - Apply artistic styles to videos
   - Adjustable style strength
   - GPU-accelerated processing

2. Video Enhancement
   - Upscale video resolution
   - Denoise video content
   - Stabilize shaky footage
   - GPU-accelerated processing

3. Text-to-Video Generation
   - Generate videos from text descriptions
   - Adjustable duration
   - AI-powered content creation

## License

This project includes components with various licenses:
- OpenShot libraries (GPLv3)
- LTX-Video model integration
- Custom Flask web application

## Contributors

- Project maintainers and contributors