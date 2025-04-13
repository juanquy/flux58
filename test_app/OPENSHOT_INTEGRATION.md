# OpenShot Integration Documentation

This document describes the integration between the FLUX58 AI MEDIA LABS web application and the OpenShot video processing libraries.

## Overview

The FLUX58 platform integrates with OpenShot libraries to provide professional video editing capabilities, enabling users to create, edit, and export video projects through a web interface.

## Components

1. **libopenshot-audio**: Handles audio processing functionality
2. **openshot-server**: Core video processing library that provides:
   - Video and audio playback
   - Timeline management
   - Effects processing
   - Video export capabilities
   - Frame manipulation
   - Transitions

## Integration Architecture

The FLUX58 platform integrates with OpenShot through a layered architecture:

```
┌─────────────────────────────────────┐
│         FLUX58 Web Interface        │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│      REST API (Flask Endpoints)     │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│         openshot_api.py             │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ Python Bindings (openshot module)   │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│ libopenshot & libopenshot-audio     │
└─────────────────────────────────────┘
```

## API Endpoints

The application provides the following REST endpoints for interacting with OpenShot functionality:

- `/api/openshot/status` - Check if OpenShot library is available
- `/api/project/<project_id>/clips` - Create clips on the timeline
- `/api/project/<project_id>/export` - Export projects to video files
- `/api/project/<project_id>/timeline/tracks` - Manage timeline tracks

## Fallback Handling

For robustness, the system implements fallback mechanisms when OpenShot is not available:

1. The web interface will display "Demo Mode" to users
2. Basic timeline functionality will still be available 
3. The editor UI will function normally but without actual video processing
4. Export operations will simulate progress but won't produce real video files

This allows users to still access the platform even if there are issues with the OpenShot libraries.

## Admin Controls

Administrators have special tools for monitoring and managing the OpenShot service:

1. **Status Monitoring**: The admin panel shows the current status of the OpenShot service
2. **Service Restart**: Admins can restart the OpenShot service if needed
3. **Status Check**: Manual verification of OpenShot availability

## Technical Implementation

### Service Initialization

The OpenShot integration is initialized when the application starts:

```python
# Try to import and initialize OpenShot API
try:
    from openshot_api import OpenShotVideoAPI, OPENSHOT_AVAILABLE
    openshot_api = OpenShotVideoAPI()
    if openshot_api.openshot_available:
        print("OpenShot library initialized successfully")
    else:
        print("Warning: OpenShot library not available, using placeholder implementation")
except ImportError as e:
    print(f"Error importing OpenShot API: {str(e)}")
    OPENSHOT_AVAILABLE = False
    openshot_api = None
```

### Python Path Configuration

OpenShot libraries are found by adding them to the Python path:

```python
# Add OpenShot library to Python path
OPENSHOT_PYTHON_PATH = "/home/juanquy/OpenShot/openshot-server/build/bindings/python"
sys.path.append(OPENSHOT_PYTHON_PATH)

# Try to import OpenShot
try:
    import openshot
    OPENSHOT_AVAILABLE = True
except ImportError:
    OPENSHOT_AVAILABLE = False
    print("Warning: OpenShot library not available. Using fallback implementation.")
```

## Clips and Timeline

Clips are created using the OpenShot API with appropriate parameter handling:

```python
# Create clip using OpenShot API if available
if openshot_api and openshot_api.openshot_available:
    # Create clip with OpenShot
    clip = openshot_api.create_clip(project_id, asset_data.get('path'), start_time, end_time)
            
    # Add to timeline database
    db_clip = project_manager.add_clip_to_timeline(
        project_id=project_id,
        asset_id=asset_id,
        track_id=track_id,
        position=position,
        duration=duration
    )
```

## Video Export

Export jobs utilize OpenShot's rendering capabilities:

```python
# Start export in background
export_data = openshot_api.export_video(
    project_id=project_id,
    output_filename=filename,
    **export_params
)
```

## Service Management

Admin tools can restart the OpenShot service when needed:

```python
# Try to restart the OpenShot service
subprocess.run(['sudo', 'systemctl', 'restart', 'libopenshot.service'], check=True)
        
# Wait a moment for the service to restart
time.sleep(2)
        
# Reinitialize the OpenShot API
from openshot_api import OpenShotVideoAPI
globals()['openshot_api'] = OpenShotVideoAPI()
```

## Installation Requirements

For full OpenShot integration, the following components must be installed:

1. libopenshot-audio
2. openshot-server
3. Python bindings for OpenShot

The application will still run without these components, but in a limited demo mode.

## Testing the Integration

To verify OpenShot integration is working properly:

1. Access the admin panel at `/admin/system`
2. Check the OpenShot Service Status card
3. Use the "Check Status" button to verify library availability
4. If needed, use "Restart Service" to reinitialize the OpenShot connection

## Troubleshooting

Common issues:

1. **Missing Libraries**: Ensure both libopenshot and libopenshot-audio are installed
2. **Python Path**: Verify the OPENSHOT_PYTHON_PATH points to the correct location
3. **Library Permissions**: Check that the libraries are accessible to the web application
4. **Service Status**: Verify the libopenshot service is running (`systemctl status libopenshot.service`)

If OpenShot integration isn't working, check the logs at `/home/juanquy/OpenShot/test_app/logs/flux58.log` for specific error messages.