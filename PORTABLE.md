# OpenShot Web Application - Portability Guide

This document explains how the application has been made portable so it can be deployed in any environment.

## Directory Structure

The application now uses relative paths based on the repository root:

```
/OpenShot/                      # Repository root
├── backups/                    # Database and application backups
├── libopenshot-audio/          # OpenShot Audio library
├── openshot-server/            # OpenShot server (libopenshot)
├── openshot_service_venv/      # Python virtual environment
└── test_app/                   # Web application
    ├── data/                   # Application data
    │   ├── exports/            # Exported videos
    │   ├── projects/           # Project files
    │   └── uploads/            # Uploaded media files
    ├── logs/                   # Application logs
    ├── static/                 # Static assets (CSS, JS, images)
    └── templates/              # HTML templates
```

## Configuration

The application uses the following configuration mechanism:

1. First, try to load from `config.py` which contains all paths and settings
2. If not available, use environment variables
3. If environment variables aren't set, use sensible defaults based on the repository structure

## Key Files

- `config.py`: Central configuration file that defines all paths
- `setupOS.sh`: Setup script that uses relative paths based on its own location
- `app.py`: Main Flask application with portable configuration
- `openshot_api.py`: OpenShot integration with portable path detection

## Important Changes

1. **Path Resolution**: All paths are now relative to the repository root
2. **Environment Variables**: Configuration can be overridden with environment variables
3. **Automatic Directory Creation**: Required directories are automatically created if missing
4. **Configuration Fallbacks**: Multiple fallback mechanisms for finding the right paths

## Setting Up in a New Environment

1. Clone the repository: `git clone https://your-repo-url.git`
2. Run the setup script: `cd OpenShot && ./setupOS.sh`
3. The script will:
   - Detect its own location and use that as the base directory
   - Install all necessary dependencies
   - Configure PostgreSQL (if requested)
   - Set up the Python virtual environment
   - Build OpenShot libraries
   - Create necessary directories

## Configuration Environment Variables

You can customize the application by setting these environment variables:

- `DB_HOST`: PostgreSQL database host (default: localhost)
- `DB_PORT`: PostgreSQL database port (default: 5432)
- `DB_NAME`: PostgreSQL database name (default: flux58)
- `DB_USER`: PostgreSQL database user (default: flux58_user)
- `DB_PASS`: PostgreSQL database password (default: flux58_password)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions
- `LOG_LEVEL`: Logging level (default: INFO)
- `EXPORT_CONCURRENT_JOBS`: Number of concurrent export jobs (default: 2)

These can be set in a `.env` file in the `test_app` directory or in the environment before starting the application.

## Running the Application

After setup:

1. Activate the virtual environment: `source openshot_service_venv/bin/activate`
2. Navigate to the app directory: `cd test_app` 
3. Run the application: `python app.py`

## Architecture-Specific Considerations

### x86_64 (March 21, 2025 Update)

The application has been successfully ported from PowerPC (ppc64le) to x86_64 architecture. Key changes include:

1. **Dependency Updates**: All required libraries rebuilt for x86_64
2. **Build Process**: Updated build instructions for x86_64 systems
3. **Library Paths**: Fixed all architecture-specific library paths
4. **Performance Optimizations**: Leverage x86_64-specific optimizations for video processing

When running on x86_64 systems:
- Hardware acceleration options are more extensive
- Compilation is generally faster than on PowerPC
- Standard package repositories can be used without special handling

### PowerPC (ppc64le)

For PowerPC architecture, the setup script includes several optimizations:

1. **Package Installation**: Additional packages like `libopenblas-dev` and `libatlas-base-dev` are installed
2. **Python Packages**: The script attempts binary installs first, then falls back to source compilation
3. **Build Parameters**: CMake is configured with `-fPIC` flags essential for PowerPC builds
4. **Build Parallelism**: Reduced to 2 cores to prevent resource exhaustion on PowerPC systems
5. **psycopg2 Installation**: Special handling for PostgreSQL adapter on PowerPC architectures

When running on PowerPC systems:
- Compilation might take longer, especially for OpenShot libraries
- Memory usage during compilation is carefully managed
- Additional system libraries might be required for optimal performance

## Building OpenShot on x86_64

To build OpenShot on x86_64 systems:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y build-essential cmake pkg-config git libzmq3-dev libffi-dev python3-dev python3-venv
sudo apt-get install -y libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libswresample-dev ffmpeg
sudo apt-get install -y libmagick++-dev libjsoncpp-dev libjpeg-dev libopencv-dev python3-opencv
sudo apt-get install -y libqt5svg5-dev qtbase5-dev qtmultimedia5-dev libasound2-dev libpulse-dev
sudo apt-get install -y libprotobuf-dev protobuf-compiler swig

# Build libopenshot-audio
cd /path/to/OpenShot
mkdir -p libopenshot-audio/build
cd libopenshot-audio/build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
make -j4
sudo make install

# Build libopenshot
cd /path/to/OpenShot
mkdir -p openshot-server/build
cd openshot-server/build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DUSE_SYSTEM_JSONCPP=1
make -j4
sudo make install
```

## Troubleshooting

If you encounter path-related issues:

1. Check the `config.py` file to ensure paths are correct
2. Verify that all required directories exist
3. Check the application logs for path-related errors
4. Make sure OpenShot libraries are properly built and in the expected locations

### x86_64-Specific Issues

If running on x86_64 and encountering issues:

1. Check for missing dependencies: `ldd /usr/lib/x86_64-linux-gnu/libopenshot.so`
2. Verify that Qt dependencies are correctly installed
3. For Python binding issues, check: `python3 -c "import openshot; print('Success')"`
4. If OpenCV features aren't working, ensure you have the development packages: `apt-get install libopencv-dev`

### PowerPC-Specific Issues

If running on PowerPC (ppc64le) and encountering issues:

1. Check system memory during OpenShot compilation - reduce parallelism further if needed
2. Verify `-fPIC` flags are being passed to the compiler
3. Try building with debug symbols: `CMAKE_CXX_FLAGS="-fPIC -g" CMAKE_C_FLAGS="-fPIC -g"`
4. For Python package issues, try manual installation with: `pip install --no-binary :all: package_name`