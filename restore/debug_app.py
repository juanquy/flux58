#!/usr/bin/env python
import os
import sys

# Force environment variables for database
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'

# Set a persistent secret key
os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_for_testing_only'

# Import the Flask app
sys.path.insert(0, '/home/juanquy/OpenShot/test_app')

# Add debug logging before importing the app
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

# Import the app
from app import app

# Enable detailed exception handling
app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == '__main__':
    # Run with debug enabled and accessible from LAN
    app.run(host='0.0.0.0', port=5000, debug=True)