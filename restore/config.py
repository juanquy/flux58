import os
import sys
import logging

# Base directory - the OpenShot project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application directories
TEST_APP_DIR = os.path.join(BASE_DIR, 'test_app')
OPENSHOT_SERVER_DIR = os.path.join(BASE_DIR, 'openshot-server')
OPENSHOT_AUDIO_DIR = os.path.join(BASE_DIR, 'libopenshot-audio')

# Data directories
DATA_DIR = os.path.join(TEST_APP_DIR, 'data')
PROJECTS_DIR = os.path.join(DATA_DIR, 'projects')
EXPORTS_DIR = os.path.join(DATA_DIR, 'exports')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
LOGS_DIR = os.path.join(TEST_APP_DIR, 'logs')
BACKUPS_DIR = os.path.join(BASE_DIR, 'backups')

# OpenShot Python path - for importing libopenshot
OPENSHOT_PYTHON_PATH = os.path.join(OPENSHOT_SERVER_DIR, 'build', 'bindings', 'python')

# Virtual environment path
VENV_DIR = os.path.join(BASE_DIR, 'openshot_service_venv')

# Create necessary directories if they don't exist
for directory in [DATA_DIR, PROJECTS_DIR, EXPORTS_DIR, UPLOADS_DIR, LOGS_DIR, BACKUPS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Add OpenShot to Python path if not already there
if OPENSHOT_PYTHON_PATH not in sys.path:
    sys.path.append(OPENSHOT_PYTHON_PATH)

# Database configuration with environment variable fallbacks
# You can override these with environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'flux58_user')
DB_PASS = os.environ.get('DB_PASS', 'flux58_password')

# Flask configuration
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
if not FLASK_SECRET_KEY:
    # Try to read from file
    secret_key_path = os.path.join(TEST_APP_DIR, '.flask_secret_key')
    try:
        if os.path.exists(secret_key_path):
            with open(secret_key_path, 'r') as f:
                FLASK_SECRET_KEY = f.read().strip()
    except Exception:
        pass
        
    # Generate if still missing
    if not FLASK_SECRET_KEY:
        import secrets
        FLASK_SECRET_KEY = secrets.token_hex(32)
        
        # Try to save for future use
        try:
            with open(secret_key_path, 'w') as f:
                f.write(FLASK_SECRET_KEY)
        except Exception:
            logging.warning("Could not save Flask secret key to file")

# Application settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
EXPORT_CONCURRENT_JOBS = int(os.environ.get('EXPORT_CONCURRENT_JOBS', '2'))