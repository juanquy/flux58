# FLUX58 AI MEDIA LABS

An AI-powered video creation and editing platform optimized for IBM POWER8 architecture.

## Overview

This service provides a complete backend for video editing in the cloud, allowing users to:

1. Create and manage video editing projects
2. Upload and manage media assets (video, audio, images)
3. Edit videos through timeline manipulation
4. Apply effects and transitions
5. Export finished videos in various formats

The platform uses a credit-based payment system where users purchase credits to pay for processing time and exports. Multiple pricing tiers are available, including a free plan option with limited features.

## Technology Stack

- **Platform**: IBM S822LC 8335 SxM2 Server (PowerPC LE architecture)
- **Hardware**: 2x10-Core Power 8 Processor, 256GB RAM, 4x NVIDIA P100 16GB GPUs
- **Backend**: Flask (Python)
- **Video Processing**: OpenShot libraries
- **Authentication**: Session-based authentication with admin impersonation
- **Database**: PostgreSQL (production-ready implementation)
- **Payment**: Credit-based system with PayPal integration
- **Frontend**: Bootstrap 5 with responsive design

## Database Support

The application uses PostgreSQL as its production database:

**PostgreSQL** - Enterprise-grade relational database offering:
- Robust transaction support
- Concurrent access for multiple users
- Proper data integrity and constraints
- Enhanced performance for video processing workloads
- Better security features for production environments

The database interface handles datetime objects correctly and provides appropriate error handling with graceful fallbacks for development environments. All database operations are performed through a unified interface that ensures consistency across the application.

## Web Interface

The application provides a complete web interface for users and administrators:

### User Dashboard
- **Dashboard**: Analytics, recent projects, and credit overview
- **Projects**: Create, manage, and edit projects
- **Editor**: Full timeline-based video editor with modern dark UI
- **Exports**: View and download exported videos
- **Credits**: Manage credits and view transaction history
- **Pricing**: View available pricing plans

### Video Editor
The editor features a modern, professional interface optimized for video editing:

- **Modern Dark UI**: Reduces eye strain during long editing sessions with elegant, professional design
- **Multi-Track Timeline**: Drag-and-drop interface with interactive tracks and clips
- **Media Library**: Organized asset management with search and AI enhancement capabilities
- **Advanced Preview**: High-quality video preview with frame-accurate navigation controls
- **Properties Panel**: Comprehensive clip settings with collapsible sections for easy access
- **AI Integration**: Direct access to AI features including enhancement and content generation
- **Interactive Controls**: Visual feedback for selections and operations with responsive UI elements
- **Progress Tracking**: Visual indicators for all processing operations

### Admin Dashboard
- **Dashboard**: System overview, analytics, and recent activity
- **User Management**: Create, edit, and manage users
- **Projects**: Manage all projects on the platform
- **Exports**: View and manage export jobs
- **System**: Monitor system health, OpenShot service status, backups, and maintenance
- **Service Management**: Check and restart OpenShot services directly from the admin panel
- **Payment Settings**: Configure payment gateways and credit packages
- **Custom Branding**: Full control over branding elements, colors, and layout
- **Landing Page Editor**: Drag-and-drop interface for customizing the landing page

## API Documentation

Full API documentation is available at the `/api/docs` endpoint.

Key endpoints:

- **Authentication**: `/api/register`, `/api/login`, `/api/logout`
- **Payments**: `/api/payment/add-credits`, `/api/credits/balance`
- **Projects**: `/api/projects`
- **Assets**: `/api/projects/<project_id>/assets`
- **Timeline**: `/api/projects/<project_id>/timeline/clips`, `/api/project/<project_id>/timeline/tracks`
- **Export**: `/api/projects/<project_id>/export`
- **OpenShot**: `/api/openshot/status`

## AI Features

### AI-Powered Video Enhancement
- Automatic video quality improvement with one-click enhancement
- Smart upscaling for low-resolution footage
- Noise reduction and stabilization
- Color correction and grading with AI presets

### Content Generation
- Text2Video generation using LTX Video AI model
- Image2Video transformation
- AI-generated music and sound effects
- Text-to-speech narration with natural voices
- Automatic captioning and transcription

### Intelligent Editing
- AI Assistant with natural language interface for editing guidance
- Smart video editing with AI-powered recommendations
- Automatic content analysis and organization
- Scene detection and smart clip arrangement
- One-click montage creation from raw footage

### Technical Implementation
- Optimized for IBM POWER8 architecture
- Enhanced GPU acceleration using NVIDIA P100 capabilities
- Parallel processing for faster rendering
- Low-latency AI processing for real-time feedback
- Expanded effects library with PowerPC-specific optimizations

## Pricing Plans

The application offers multiple pricing tiers:

| Plan | Price | Credits | Storage | Support |
|------|-------|---------|---------|---------|
| Free | $0 | 50 | 2.5GB | None |
| Starter | $9.99 | 100 | 5GB | Email |
| Professional | $19.99 | 300 | 15GB | Priority Email |
| Enterprise | $49.99 | 1000 | 50GB | Phone |

### Credit Usage

| Feature | Credits |
|---------|---------|
| 720p Export | 5 |
| 1080p Export | 10 |
| 4K Export | 20 |
| Text to Video | 30 |
| Image to Video | 25 |
| AI Enhancement | 15 |

## Getting Started

1. Register an account at `/register` or using `/api/register` API endpoint
2. Login to access your dashboard
3. Purchase credits or use free credits
4. Create your first project
5. Upload media assets and start editing!

## Installation and Setup

### Updated Setup (March 21, 2025)

The PostgreSQL database has been successfully configured with:
- Database: `flux58`
- User: `flux58_user`
- Password: `flux58_password`

To run the application:

```bash
# Navigate to application directory
cd /root/OpenShot/test_app

# Activate virtual environment
source venv/bin/activate

# Run the application
python flux58.py
```

### Latest Backups
- Application backup: `/root/OpenShot/test_app/backups/20250321/flux58_app_20250321_203916.tar.gz`
- Database backup: `/root/OpenShot/test_app/backups/20250321/flux58_db_20250321_204015.sql`

If port 5000 is already in use, specify an alternative port:

```bash
PORT=5001 python flux58.py
```

### Complete Manual Setup

If you need to set up the application from scratch:

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up PostgreSQL 
sudo -i -u postgres psql -c "CREATE USER flux58_user WITH PASSWORD 'flux58_password' CREATEDB;"
sudo -i -u postgres psql -c "CREATE DATABASE flux58;"
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE flux58 TO flux58_user;"
sudo -i -u postgres psql -d flux58 -c "GRANT ALL ON SCHEMA public TO flux58_user;"

# Initialize the database
python init_postgres.py

# Run the application
python flux58.py
```

## Configuration

The application now uses environment variables automatically set in `flux58.py` for configuration:

```python
# Database Configuration
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'

# Flask Configuration
os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_for_testing_only'
```

Additional configuration can be set in a `.env` file or `env_production` for other settings:

```
# PayPal Configuration (for payment processing)
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com  # Use https://api-m.paypal.com for production

# Application Settings
LOG_LEVEL=INFO
EXPORT_CONCURRENT_JOBS=2
```

## Testing PostgreSQL Connection

The PostgreSQL connection has been verified and is working properly. If you need to test it again:

```bash
cd /root/OpenShot/test_app
source venv/bin/activate
python test_postgres.py
```

To access the admin interface:
- URL: http://localhost:5000/admin
- Username: admin
- Password: admin123

## Documentation

- For PostgreSQL-specific information, see [POSTGRES.md](POSTGRES.md)
- For editor UI details and features, see [EDITOR_UI.md](EDITOR_UI.md)
- For AI capabilities and implementation, see [AI_FEATURES.md](AI_FEATURES.md)
- For OpenShot integration details, see [OPENSHOT_INTEGRATION.md](OPENSHOT_INTEGRATION.md)
- The database adapter is implemented in [database.py](database.py) and [postgres_db.py](postgres_db.py)

The server will start at `http://0.0.0.0:5000`

## Maintenance

- Database backups are stored in the `test_app/backups/` directory
- Full project backups are stored in the `/home/juanquy/OpenShot/backups/` directory
- Logs are stored in the `test_app/logs/` directory
- Media files are stored in the `test_app/data/` directory

## Recent Updates

### 2025-03-21
- Fixed PostgreSQL configuration with proper user permissions
- Resolved Flask module import errors by properly activating virtual environment
- Updated database credentials in initialization scripts
- Fixed port conflicts with alternative port usage
- Updated documentation with PostgreSQL setup instructions
- Enhanced error handling in database connection code

### 2025-03-19
- Created flux58.py launcher script for improved reliability
- Fixed format string errors in multiple functions throughout the application
- Created comprehensive backups of application code and database
- Improved error handling for important system functions

### 2025-03-16
- Implemented OpenShot server integration for real video processing capabilities
- Added OpenShot service status monitoring in admin panel
- Created OpenShot service management tools with restart functionality
- Properly integrated PostgreSQL for production environment
- Fixed editor loading issues and improved error handling
- Added RESTful API endpoints for OpenShot functionality:
  - `/api/openshot/status` - Check OpenShot availability
  - `/api/project/<project_id>/clips` - Create clips on timeline
  - `/api/project/<project_id>/export` - Export projects to video files
  - `/api/project/<project_id>/timeline/tracks` - Manage timeline tracks
- Enhanced frontend JavaScript to interact with OpenShot API endpoints
- Improved database connection handling with proper fallback mechanisms
- Created comprehensive admin system with monitoring tools
- Added backup system for application and database
- Fixed all references to SQLite to consistently use PostgreSQL
- Developed a robust editor loading system that works even without OpenShot
- Created emergency project recovery functionality
- Improved session management and authentication

### 2025-03-15
- Modern UI for OpenShot editor with dark theme optimized for video editing
- Added AI interface elements to showcase POWER8 AI capabilities
- Enhanced timeline functionality with interactive playhead and time markers
- Improved clip management with visual selection indicators
- Added collapsible panel system for better screen space utilization
- Integrated dynamic asset library with AI enhancement options
- Improved export workflow with detailed progress tracking
- Responsive notifications system with visual feedback
- Added AI Assistant feature with natural language interface
- Implemented visual upload interface with drag-and-drop support
- Migrated from SQLite to PostgreSQL for improved reliability and concurrency
- Fixed database threading issues with proper connection management
- Added free plan option (50 credits, 2.5GB storage, no support)
- Enhanced pricing page UI with better layout and hover effects
- Fixed user management interface in admin panel
- Improved datetime handling for consistent display across database backends
- Fixed admin payment settings page
- Updated documentation with current system architecture details

### Known Issues
- OpenShot API requires proper installation of libopenshot and libopenshot-audio
- The system will fall back to a demo mode if OpenShot libraries aren't available
- PayPal API requires valid credentials for full testing
- When adding a new user, make sure to grant initial credits