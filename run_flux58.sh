#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Set base directory
BASE_DIR="/root/OpenShot"
APP_DIR="${BASE_DIR}/test_app"
VENV_DIR="${APP_DIR}/venv"
LOG_FILE="${APP_DIR}/logs/flux58.log"
OPENSHOT_DIR="${BASE_DIR}/openshot-server"
OPENSHOT_AUDIO_DIR="${BASE_DIR}/libopenshot-audio"

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  FLUX58 AI MEDIA LABS - LAUNCHER    ${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${YELLOW}Starting with enhanced environment check...${NC}"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Error: Application directory not found: $APP_DIR${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p "${APP_DIR}/logs"

# Change to app directory
cd "$APP_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Virtual environment not found at $VENV_DIR${NC}"
    echo -e "${YELLOW}Creating new virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "${RED}Failed to create virtual environment. Please install python3-venv package.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating Python virtual environment...${NC}"
source "${VENV_DIR}/bin/activate"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment!${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}Using $PYTHON_VERSION${NC}"

# Install dependencies if needed
if [ -f "${APP_DIR}/requirements.txt" ]; then
    echo -e "${YELLOW}Checking Python dependencies...${NC}"
    
    # Install dependencies
    pip install -q -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies!${NC}"
        exit 1
    else
        echo -e "${GREEN}Dependencies installed successfully.${NC}"
    fi
else
    echo -e "${YELLOW}No requirements.txt found, skipping dependency installation.${NC}"
fi

# Check PostgreSQL connection
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, dbname='flux58', user='flux58_user', password='flux58_password'); conn.close(); print('PostgreSQL connection successful')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}PostgreSQL connection failed! Checking if PostgreSQL is running...${NC}"
    if command -v systemctl &> /dev/null; then
        # For systemd-based systems
        if ! systemctl is-active --quiet postgresql; then
            echo -e "${YELLOW}Starting PostgreSQL service...${NC}"
            sudo systemctl start postgresql
            sleep 2
        fi
    elif command -v service &> /dev/null; then
        # For init.d-based systems
        if ! service postgresql status &> /dev/null; then
            echo -e "${YELLOW}Starting PostgreSQL service...${NC}"
            sudo service postgresql start
            sleep 2
        fi
    fi
    
    # Check connection again
    python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port=5432, dbname='flux58', user='flux58_user', password='flux58_password'); conn.close(); print('PostgreSQL connection successful')" 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Still unable to connect to PostgreSQL. Please check your database setup.${NC}"
        echo -e "${YELLOW}Database credentials used: flux58_user / flux58_password${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}PostgreSQL connection successful.${NC}"
fi

# Create file for OpenShot library fix
cat > "${APP_DIR}/fix_openshot.py" << 'EOL'
#!/usr/bin/env python3
"""
OpenShot library fix script - sets up OpenShot Python bindings
"""
import os
import sys
import platform
import site
import shutil
import subprocess
from pathlib import Path

def main():
    """
    Main function to fix OpenShot library issues
    """
    print("Setting up OpenShot Library Python bindings...")
    
    # First, set environment variables
    os.environ["LD_LIBRARY_PATH"] = os.environ.get("LD_LIBRARY_PATH", "") + ":/usr/lib:/usr/local/lib"
    print(f"Set LD_LIBRARY_PATH: {os.environ['LD_LIBRARY_PATH']}")

    # Add common paths where OpenShot bindings might be
    potential_paths = [
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3/dist-packages",
        "/usr/lib/python3.8/site-packages",
        "/usr/local/lib/python3.8/site-packages",
        os.path.expanduser("~/OpenShot/openshot-server/build/src/bindings/python"),
        "/root/OpenShot/openshot-server/build/src/bindings/python"
    ]
    
    # Add paths to sys.path if they exist
    for path in potential_paths:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            print(f"Added path to Python: {path}")
    
    # Check if OpenShot libraries exist
    lib_paths = {
        "libopenshot.so": ["/usr/lib/libopenshot.so", "/usr/local/lib/libopenshot.so"],
        "libopenshot-audio.so": ["/usr/lib/libopenshot-audio.so", "/usr/local/lib/libopenshot-audio.so"]
    }
    
    libs_found = True
    for lib_name, paths in lib_paths.items():
        found = False
        for path in paths:
            if os.path.exists(path):
                print(f"Found {lib_name} at {path}")
                found = True
                break
        if not found:
            print(f"WARNING: {lib_name} not found in standard locations")
            libs_found = False
    
    # Try to import OpenShot to verify binding installation
    try:
        import openshot
        print(f"OpenShot Python binding imported successfully: {openshot.OPENSHOT_VERSION_FULL}")
        
        # Test a basic operation to verify it's working
        try:
            color = openshot.Color()
            print("OpenShot library functionality verified (created Color object)")
            return True
        except Exception as e:
            print(f"WARNING: OpenShot library imported but functionality test failed: {str(e)}")
    except ImportError as e:
        print(f"WARNING: Failed to import OpenShot Python bindings: {str(e)}")
        
        if libs_found:
            print("\nThe OpenShot libraries are installed but Python bindings are not working.")
            print("This is likely because the bindings weren't properly compiled or installed.")
            print("\nCreating symlink to system OpenShot bindings in virtual environment...")
            
            # Try to find the system openshot.so file
            openshot_so = None
            for path in potential_paths:
                potential_so = os.path.join(path, "openshot.so")
                if os.path.exists(potential_so):
                    openshot_so = potential_so
                    break
            
            if openshot_so:
                # Get the site-packages directory of the current virtual environment
                site_packages = site.getsitepackages()[0]
                try:
                    # Create a symlink to the system openshot.so
                    target = os.path.join(site_packages, "openshot.so")
                    print(f"Creating symlink from {openshot_so} to {target}")
                    if os.path.exists(target):
                        os.remove(target)
                    os.symlink(openshot_so, target)
                    print("Symlink created successfully!")
                    
                    # Try to import again after creating the symlink
                    try:
                        import openshot
                        print(f"SUCCESS! OpenShot Python binding imported successfully after fix: {openshot.OPENSHOT_VERSION_FULL}")
                        return True
                    except ImportError as e:
                        print(f"Still unable to import OpenShot after symlink: {str(e)}")
                except Exception as e:
                    print(f"Error creating symlink: {str(e)}")
            else:
                print("Could not find openshot.so file in system paths")
        
        print("\nUnable to fix OpenShot Python bindings. The application will run in fallback mode.")
        
    return False

if __name__ == "__main__":
    main()
EOL

# Check for flux58.py
if [ ! -f "${APP_DIR}/flux58.py" ]; then
    echo -e "${RED}Error: flux58.py not found in ${APP_DIR}${NC}"
    exit 1
fi

# Check and attempt to fix OpenShot library
echo -e "${YELLOW}Checking and fixing OpenShot library integration...${NC}"
python "${APP_DIR}/fix_openshot.py"
export LD_LIBRARY_PATH="/usr/lib:/usr/local/lib:${LD_LIBRARY_PATH}"

# Check if we can now import OpenShot
echo -e "${YELLOW}Verifying OpenShot library...${NC}"
python -c "import openshot; print(f'OpenShot version: {openshot.OPENSHOT_VERSION_FULL}')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}OpenShot library not available. The app will use a placeholder implementation.${NC}"
    echo -e "${YELLOW}Some video editing features will be limited.${NC}"
else
    echo -e "${GREEN}OpenShot library found and loaded.${NC}"
fi

# Set up link for automatic library loading
if [ -d "$VENV_DIR/lib" ]; then
    # Create .pth file to add OpenShot library paths
    echo -e "${YELLOW}Creating path file for OpenShot libraries...${NC}"
    echo "/usr/lib/python3/dist-packages" > "$VENV_DIR/lib/python3.8/site-packages/openshot.pth"
    echo "/usr/local/lib/python3/dist-packages" >> "$VENV_DIR/lib/python3.8/site-packages/openshot.pth"
    echo "/root/OpenShot/openshot-server/build/src/bindings/python" >> "$VENV_DIR/lib/python3.8/site-packages/openshot.pth"
fi

# Default port
PORT=${PORT:-5090}

# Check if port is already in use
if command -v nc &> /dev/null; then
    nc -z localhost $PORT &>/dev/null
    PORT_IN_USE=$?
    if [ $PORT_IN_USE -eq 0 ]; then
        echo -e "${RED}Port $PORT is already in use!${NC}"
        exit 1
    fi
elif command -v lsof &> /dev/null; then
    if lsof -i :$PORT &>/dev/null; then
        echo -e "${RED}Port $PORT is already in use!${NC}"
        exit 1
    fi
fi

# Set environment variables
export FLASK_APP=flux58.py
export FLASK_ENV=development
export PORT=$PORT

echo -e "${GREEN}All checks passed! Starting Flux58 on port $PORT...${NC}"
echo -e "${GREEN}Access the application at http://localhost:$PORT${NC}"
echo -e "${GREEN}--------------------------------------------${NC}"

# Run the application
python flux58.py

# If we got here, the application terminated
echo -e "${YELLOW}Application terminated. Check logs for details: $LOG_FILE${NC}"