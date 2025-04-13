#!/bin/bash

set -e

# Get the absolute path to the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"

# Error handling function
handle_error() {
    echo "Error on line $1"
    exit 1
}
trap 'handle_error $LINENO' ERR

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default build settings
BUILD_JOBS=$(nproc)

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}     FLUX58 AI MEDIA LABS Setup                     ${NC}"
echo -e "${BLUE}====================================================${NC}"
echo -e "${GREEN}Base Directory: $BASE_DIR${NC}"

# Update and install dependencies
echo -e "${YELLOW}Updating system and installing dependencies...${NC}"
sudo apt update && sudo apt upgrade -y

# Check and install required packages - with better error handling
REQUIRED_PKGS=("python3" "python3-pip" "python3-venv" "python3-dev" "git" "ffmpeg" "build-essential" "cmake" "qtbase5-dev" "qttools5-dev-tools" "libqt5svg5-dev" "libavcodec-dev" "libavformat-dev" "libavutil-dev" "libswscale-dev" "libavdevice-dev" "libjsoncpp-dev" "libprotobuf-dev" "protobuf-compiler" "libopencv-dev" "libasound2-dev" "libzmq3-dev" "imagemagick" "librsvg2-dev" "libmagick++-dev" "swig" "libbabl-dev" "postgresql" "postgresql-contrib" "gunicorn")

# Architecture check
ARCH=$(uname -m)
echo -e "${BLUE}Detected architecture: $ARCH${NC}"
if [[ "$ARCH" == "ppc64le" ]]; then
    echo -e "${YELLOW}PowerPC architecture detected. Installing ppc64le specific packages...${NC}"
    # Add PowerPC specific packages here
    ADDITIONAL_PKGS=("libopenblas-dev" "libatlas-base-dev")
    REQUIRED_PKGS=("${REQUIRED_PKGS[@]}" "${ADDITIONAL_PKGS[@]}")
    
    # Check available memory for build process
    TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
    echo -e "${BLUE}Available memory: ${TOTAL_MEM}MB${NC}"
    
    if (( TOTAL_MEM < 4000 )); then
        echo -e "${YELLOW}Limited memory detected (<4GB). Build process will be optimized for low memory.${NC}"
        # Set environment variable to limit memory usage during build
        export CFLAGS="-O2 -g0"
        export CXXFLAGS="-O2 -g0"
        # Use less cores for build to avoid out of memory
        BUILD_JOBS=1
    else
        BUILD_JOBS=2
    fi
    
    echo -e "${BLUE}Build will use ${BUILD_JOBS} core(s) on PowerPC${NC}"
fi

# Install packages with better error handling
for pkg in "${REQUIRED_PKGS[@]}"; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        echo -e "${YELLOW}Installing $pkg...${NC}"
        if sudo apt install -y "$pkg"; then
            echo -e "${GREEN}Successfully installed $pkg.${NC}"
        else
            echo -e "${RED}Failed to install $pkg. Checking if it's essential...${NC}"
            # List of essential packages that must be installed
            ESSENTIAL=("python3" "python3-pip" "python3-venv" "git" "build-essential" "cmake")
            if [[ " ${ESSENTIAL[*]} " =~ " ${pkg} " ]]; then
                echo -e "${RED}Error: Essential package $pkg could not be installed. Aborting.${NC}"
                exit 1
            else
                echo -e "${YELLOW}Non-essential package $pkg failed to install. Continuing anyway...${NC}"
            fi
        fi
    else
        echo -e "${GREEN}$pkg is already installed. Skipping.${NC}"
    fi
done

# Python 2.7 is no longer available in modern Ubuntu
echo -e "${YELLOW}Python 2.7 is not available in modern Ubuntu. The application will use Python 3 only.${NC}"
PYTHON2_AVAILABLE=false

# Setup PostgreSQL
setup_postgresql() {
    echo -e "\n${YELLOW}Setting up PostgreSQL...${NC}"
  
    # Check if PostgreSQL is running
    if sudo systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}PostgreSQL is already running.${NC}"
    else
        echo -e "${YELLOW}Starting PostgreSQL...${NC}"
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    fi
  
    # Create database and user
    echo -e "\n${YELLOW}Creating database and user...${NC}"
  
    # Default values
    DB_NAME="flux58"
    DB_USER="flux58_user"
    DB_PASS="flux58_password"
  
    # Check if database already exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
        echo -e "${GREEN}Database $DB_NAME already exists.${NC}"
    else
        echo -e "${YELLOW}Creating database $DB_NAME...${NC}"
        sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
        echo -e "${GREEN}Database created.${NC}"
    fi
  
    # Check if user already exists
    if sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        echo -e "${GREEN}User $DB_USER already exists.${NC}"
    else
        echo -e "${YELLOW}Creating user $DB_USER...${NC}"
        sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
        echo -e "${GREEN}User created with permissions.${NC}"
    fi
  
    # Create .env file with PostgreSQL config
    TEST_APP_DIR="$BASE_DIR/test_app"
    echo -e "\n${YELLOW}Creating .env file with PostgreSQL configuration...${NC}"
    cat > "$TEST_APP_DIR/.env" << EOF
# Database Configuration
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASS=$DB_PASS

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=app.py

# Application Settings
LOG_LEVEL=INFO
EXPORT_CONCURRENT_JOBS=2
EOF

    echo -e "${GREEN}PostgreSQL setup complete!${NC}"
}

# Set up paths for various components
TEST_APP_DIR="$BASE_DIR/test_app"
OPENSHOT_AUDIO_DIR="$BASE_DIR/libopenshot-audio"
OPENSHOT_DIR="$BASE_DIR/openshot-server"
VENV_DIR="$BASE_DIR/openshot_service_venv"
OPENSHOT_SERVICE_DIR="$BASE_DIR/openshot_service"

# Create necessary directories
mkdir -p "$BASE_DIR/backups"
mkdir -p "$TEST_APP_DIR/data/projects"
mkdir -p "$TEST_APP_DIR/data/exports"
mkdir -p "$TEST_APP_DIR/data/uploads"
mkdir -p "$TEST_APP_DIR/logs"
mkdir -p "$TEST_APP_DIR/backups/$(date +%Y%m%d)"
mkdir -p "$OPENSHOT_SERVICE_DIR/instance"

# Create virtual environment
echo -e "${YELLOW}Setting up virtual environment at $VENV_DIR...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# Install Python packages with better error handling
echo -e "${YELLOW}Installing Python packages...${NC}"
$VENV_DIR/bin/pip install --upgrade pip

# Define required Python packages
PY_PACKAGES=("flask" "flask-login" "flask-sqlalchemy" "python-dotenv" "pillow" "requests" "werkzeug" "gunicorn")

# Add architecture-specific considerations
if [[ "$ARCH" == "ppc64le" ]]; then
    echo -e "${YELLOW}Installing psycopg2 with custom build flags for PowerPC...${NC}"
    # Install build dependencies for psycopg2
    sudo apt-get install -y libpq-dev gcc
    # Try binary package first, fallback to source compilation
    if ! $VENV_DIR/bin/pip install psycopg2-binary; then
        echo -e "${YELLOW}Binary install failed, trying to build from source...${NC}"
        $VENV_DIR/bin/pip install psycopg2 --no-binary :all:
    fi
else
    # For non-PowerPC systems
    PY_PACKAGES+=("psycopg2-binary")
fi

# Install each package with error handling
for pkg in "${PY_PACKAGES[@]}"; do
    echo -e "${YELLOW}Installing $pkg...${NC}"
    if $VENV_DIR/bin/pip install $pkg; then
        echo -e "${GREEN}Successfully installed $pkg.${NC}"
    else
        echo -e "${RED}Failed to install $pkg. Checking if it's essential...${NC}"
        # Essential Python packages
        ESSENTIAL_PY=("flask" "flask-login" "flask-sqlalchemy")
        if [[ " ${ESSENTIAL_PY[*]} " =~ " ${pkg} " ]]; then
            echo -e "${RED}Error: Essential package $pkg could not be installed. Aborting.${NC}"
            exit 1
        else
            echo -e "${YELLOW}Non-essential package $pkg failed to install. Continuing anyway...${NC}"
        fi
    fi
done

# Set up PostgreSQL automatically
setup_postgresql

# Function to handle build errors
build_error_handler() {
    local component=$1
    echo -e "${RED}Error building $component. Do you want to continue anyway? [y/N]${NC}"
    read -p "" -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborting installation.${NC}"
        exit 1
    else
        echo -e "${YELLOW}Continuing despite build error for $component.${NC}"
        echo -e "${YELLOW}Note: The application may not function correctly.${NC}"
    fi
}

# Clone and build OpenShotAudio from source
echo -e "${YELLOW}Cloning/Building OpenShotAudio repository...${NC}"
if [ ! -d "$OPENSHOT_AUDIO_DIR" ]; then
    git clone https://github.com/OpenShot/libopenshot-audio.git "$OPENSHOT_AUDIO_DIR"
fi
cd "$OPENSHOT_AUDIO_DIR"
rm -rf build && mkdir -p build && cd build

# PowerPC-specific CMake options for OpenShot Audio
if [[ "$ARCH" == "ppc64le" ]]; then
    echo -e "${YELLOW}Configuring CMake for PowerPC architecture...${NC}"
    # Add PowerPC-specific options
    # -fPIC: Position Independent Code required for PowerPC
    # -O2: Optimize for performance but not at the expense of compilation time
    # -DCMAKE_BUILD_TYPE=Release: Optimized release build
    cmake .. \
        -DCMAKE_CXX_FLAGS="-fPIC -O2" \
        -DCMAKE_C_FLAGS="-fPIC -O2" \
        -DCMAKE_BUILD_TYPE=Release \
        || build_error_handler "libopenshot-audio (configure)"
else
    cmake .. || build_error_handler "libopenshot-audio (configure)"
fi

# Build with appropriate parallelism
if [[ "$ARCH" == "ppc64le" ]]; then
    echo -e "${YELLOW}Building with reduced parallelism for PowerPC (${BUILD_JOBS} cores)...${NC}"
    make -j${BUILD_JOBS} || build_error_handler "libopenshot-audio (build)"
else
    make -j$(nproc) || build_error_handler "libopenshot-audio (build)"
fi

sudo make install || build_error_handler "libopenshot-audio (install)"

# Clone and build OpenShot from source
echo -e "${YELLOW}Cloning/Building OpenShot repository...${NC}"
if [ ! -d "$OPENSHOT_DIR" ]; then
    git clone https://github.com/OpenShot/libopenshot.git "$OPENSHOT_DIR"
fi
cd "$OPENSHOT_DIR"
rm -rf build && mkdir -p build && cd build

# PowerPC-specific CMake options for OpenShot
if [[ "$ARCH" == "ppc64le" ]]; then
    echo -e "${YELLOW}Configuring CMake for PowerPC architecture...${NC}"
    # Add PowerPC-specific options
    # -fPIC: Position Independent Code required for PowerPC
    # -O2: Optimize for performance but not at the expense of compilation time
    # -DENABLE_TESTS=OFF: Skip tests to speed up build
    # -DCMAKE_BUILD_TYPE=Release: Optimized release build
    cmake .. \
        -DCMAKE_CXX_FLAGS="-fPIC -O2" \
        -DCMAKE_C_FLAGS="-fPIC -O2" \
        -DENABLE_TESTS=OFF \
        -DCMAKE_BUILD_TYPE=Release \
        || build_error_handler "libopenshot (configure)"
else
    cmake .. || build_error_handler "libopenshot (configure)"
fi

# Build with appropriate parallelism
if [[ "$ARCH" == "ppc64le" ]]; then
    echo -e "${YELLOW}Building with reduced parallelism for PowerPC (${BUILD_JOBS} cores)...${NC}"
    make -j${BUILD_JOBS} || build_error_handler "libopenshot (build)"
else
    make -j$(nproc) || build_error_handler "libopenshot (build)"
fi

sudo make install || build_error_handler "libopenshot (install)"

echo -e "${GREEN}OpenShot libraries built and installed successfully.${NC}"

# Function to check if a port is in use
check_port() {
    local PORT=$1
    netstat -tuln | grep -q ":$PORT "
    return $?
}

# Function to get PID using a port
get_pid_using_port() {
    local PORT=$1
    local PID=""
    
    # Try lsof first (common on Unix/Linux)
    if command -v lsof &> /dev/null; then
        PID=$(lsof -ti :$PORT)
    # Try netstat as fallback
    elif command -v netstat &> /dev/null; then
        PID=$(netstat -tlnp 2>/dev/null | grep ":$PORT " | awk '{print $7}' | cut -d'/' -f1)
    fi
    
    echo "$PID"
}

# Now run the OpenShot service
echo -e "${YELLOW}Starting OpenShot service...${NC}"

# Default port
PORT=${PORT:-5000}

# Check if port is in use
if check_port $PORT; then
    PID=$(get_pid_using_port $PORT)
    if [ -n "$PID" ]; then
        echo -e "${YELLOW}Port $PORT is already in use by process ID $PID${NC}"
        read -p "Do you want to kill this process and continue? (y/n): " KILL_PROCESS
        if [[ "$KILL_PROCESS" == "y" ]]; then
            echo -e "${YELLOW}Killing process $PID...${NC}"
            kill $PID
            sleep 2
            
            # Check if process is still running
            if ps -p $PID > /dev/null; then
                echo -e "${YELLOW}Process still running. Trying with more force...${NC}"
                kill -9 $PID
                sleep 2
                
                if ps -p $PID > /dev/null; then
                    echo -e "${RED}Failed to kill process. Please kill it manually or use a different port.${NC}"
                    echo -e "${YELLOW}To use a different port: PORT=5001 $0${NC}"
                    exit 1
                fi
            fi
            
            echo -e "${GREEN}Process killed. Port $PORT is now available.${NC}"
        else
            echo -e "${YELLOW}Do you want to use a different port? (y/n): ${NC}"
            read USE_DIFFERENT_PORT
            if [[ "$USE_DIFFERENT_PORT" == "y" ]]; then
                # Try ports 5001-5010
                for ALT_PORT in {5001..5010}; do
                    if ! check_port $ALT_PORT; then
                        PORT=$ALT_PORT
                        echo -e "${GREEN}Using alternative port: $PORT${NC}"
                        break
                    fi
                done
                
                if [ $PORT -eq 5000 ]; then
                    echo -e "${RED}All alternative ports are in use. Please free a port and try again.${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}Exiting without starting the application.${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}Port $PORT is in use, but couldn't identify the process.${NC}"
        echo -e "${YELLOW}Do you want to use a different port? (y/n): ${NC}"
        read USE_DIFFERENT_PORT
        if [[ "$USE_DIFFERENT_PORT" == "y" ]]; then
            # Try ports 5001-5010
            for ALT_PORT in {5001..5010}; do
                if ! check_port $ALT_PORT; then
                    PORT=$ALT_PORT
                    echo -e "${GREEN}Using alternative port: $PORT${NC}"
                    break
                fi
            done
            
            if [ $PORT -eq 5000 ]; then
                echo -e "${RED}All alternative ports are in use. Please free a port and try again.${NC}"
                exit 1
            fi
        else
            echo -e "${RED}Exiting without starting the application.${NC}"
            exit 1
        fi
    fi
fi

# Set environment variables
export FLASK_APP=$OPENSHOT_SERVICE_DIR/app.py
export FLASK_ENV=development
export SECRET_KEY=dev_key_for_testing
export PORT=$PORT

# Determine which app to run
if [ -f "$TEST_APP_DIR/flux58.py" ]; then
    echo -e "${GREEN}Starting FLUX58 application on port $PORT...${NC}"
    cd $TEST_APP_DIR
    $VENV_DIR/bin/python flux58.py
elif [ -d "$OPENSHOT_SERVICE_DIR" ] && [ -f "$OPENSHOT_SERVICE_DIR/app.py" ]; then
    echo -e "${GREEN}Starting OpenShot service on port $PORT...${NC}"
    cd $OPENSHOT_SERVICE_DIR
    $VENV_DIR/bin/python app.py
else
    echo -e "${RED}Error: Could not find application entry point.${NC}"
    echo -e "${YELLOW}Looking for either:${NC}"
    echo -e "${YELLOW}- $TEST_APP_DIR/flux58.py${NC}"
    echo -e "${YELLOW}- $OPENSHOT_SERVICE_DIR/app.py${NC}"
    exit 1
fi