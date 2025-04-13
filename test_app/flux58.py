#!/usr/bin/env python3
import os
import sys
import uuid
from datetime import datetime

# Force environment variables for database
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'

# Set a persistent secret key
os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_for_testing_only'

# Import the Flask app - use correct path for the script location
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Add debug logging before importing the app
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)

# Check if PostgreSQL is available
try:
    import psycopg2
    logging.info("PostgreSQL database module loaded successfully")
    
    # Check if we need to create a default admin user
    def create_default_admin():
        try:
            # Connect to PostgreSQL using our configured user instead of postgres superuser
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="flux58",
                user="flux58_user",
                password="flux58_password"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """)
            
            if cursor.fetchone()[0]:
                # Check if any user exists
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                
                if user_count == 0:
                    # Create default admin user
                    from werkzeug.security import generate_password_hash
                    admin_id = str(uuid.uuid4())
                    username = "admin"
                    password = "admin123"
                    password_hash = generate_password_hash(password)
                    email = "admin@example.com"
                    role = "admin"
                    now = datetime.now()
                    
                    # Insert admin user
                    cursor.execute("""
                        INSERT INTO users (id, username, password_hash, email, created_at, role)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (admin_id, username, password_hash, email, now, role))
                    
                    # Add credits
                    cursor.execute("""
                        INSERT INTO credits (user_id, total, used)
                        VALUES (%s, %s, %s)
                    """, (admin_id, 1000, 0))
                    
                    print(f"Created default admin user: {username} / {password}")
                    logging.info(f"Created default admin user: {username}")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error checking/creating admin user: {str(e)}")
            logging.error(f"Error checking/creating admin user: {str(e)}")
    
    # Try to create admin user
    create_default_admin()
    
except ImportError:
    logging.error("PostgreSQL database module not found")
except Exception as e:
    logging.error(f"Database error: {str(e)}")

# Import the app
from app import app

# Enable detailed exception handling
app.config['PROPAGATE_EXCEPTIONS'] = True

# Print initialization message
print("Configuration loaded from config.py")
print("Initializing OpenShot library...")
try:
    import openshot
    print(f"OpenShot version: {openshot.OPENSHOT_VERSION_FULL}")
    print("OpenShot library initialized successfully")
except ImportError:
    print("Warning: OpenShot library not found, using placeholder implementation")

# Print database information
print(f"Using PostgreSQL database: {os.environ['DB_NAME']} on {os.environ['DB_HOST']}:{os.environ['DB_PORT']}")

# Ensure we're using the newest app.py code
print("Initializing OpenShot library...")
try:
    import openshot
    print(f"OpenShot version: {openshot.OPENSHOT_VERSION_FULL}")
except ImportError:
    print("Warning: OpenShot library not found, using placeholder implementation")

# Print debug info about project manager
try:
    from flux58_app import ProjectManager, Database
    print("Using demo project manager for testing")
except ImportError:
    print("Could not import ProjectManager")

def check_port_in_use(port):
    """Check if a port is in use"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_process_using_port(port):
    """Get process using a port"""
    import subprocess
    try:
        # Try using lsof (Linux/Mac)
        cmd = f"lsof -i :{port} -t"
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        if output:
            return output.split('\n')[0]
    except subprocess.CalledProcessError:
        try:
            # Try using netstat (Linux)
            cmd = f"netstat -nlp | grep :{port} | awk '{{print $7}}' | cut -d'/' -f1"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            if output:
                return output.split('\n')[0]
        except subprocess.CalledProcessError:
            pass
    return None

if __name__ == '__main__':
    # Check if port 5090 is already in use
    port = 5090
    if check_port_in_use(port):
        pid = get_process_using_port(port)
        if pid:
            print(f"\033[91mERROR: Port {port} is already in use by process ID {pid}\033[0m")
            print(f"\033[93mTo kill the process, run: kill {pid}\033[0m")
            print(f"\033[93mOr to start on a different port, run: PORT=5091 python3 flux58.py\033[0m")
            sys.exit(1)
        else:
            print(f"\033[91mERROR: Port {port} is already in use, but couldn't identify the process\033[0m")
            print(f"\033[93mTo start on a different port, run: PORT=5091 python3 flux58.py\033[0m")
            sys.exit(1)
    
    # Get port from environment variable if specified
    port = int(os.environ.get('PORT', '5090'))
    print(f"Starting server on port {port}...")
    
    # Run without debug mode to avoid multiple processes
    app.run(host='0.0.0.0', port=port, debug=False)