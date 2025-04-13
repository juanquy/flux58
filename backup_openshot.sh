#!/bin/bash

# Script to automate OpenShot project backup using rsync and SSH
# This script will set up SSH keys if needed and perform rsync backup

# Configuration
SOURCE_DIR="/home/juanquy/OpenShot/"
DEST_HOST="192.168.200.103"
DEST_USER="juanquy"
DEST_DIR="/home/juanquy/OpenShot_Backup/"
LOG_FILE="/home/juanquy/openshot_backup.log"
SSH_KEY_PATH="$HOME/.ssh/id_rsa"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function for logging and console output
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Echo to console
    if [[ $level == "ERROR" ]]; then
        echo -e "${RED}[ERROR]${NC} $message"
    elif [[ $level == "SUCCESS" ]]; then
        echo -e "${GREEN}[SUCCESS]${NC} $message"
    else
        echo -e "${YELLOW}[INFO]${NC} $message"
    fi
    
    # Log to file
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Create log directory if it doesn't exist
log_message "INFO" "Starting OpenShot backup process"

# Check if SSH key exists, if not create it
if [[ ! -f "$SSH_KEY_PATH" ]]; then
    log_message "INFO" "SSH key not found. Generating new SSH key pair..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -q
    
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to generate SSH key pair"
        exit 1
    fi
    
    log_message "SUCCESS" "SSH key pair generated successfully"
fi

# Check if SSH key is installed on the remote server
# Using ssh-keyscan to add host key to known_hosts if not already there
ssh-keyscan -H "$DEST_HOST" >> ~/.ssh/known_hosts 2>/dev/null

# Try to copy the SSH key to the remote server if not already set up
# This command will prompt for password if key isn't installed
log_message "INFO" "Checking SSH key installation on remote server..."
ssh -o BatchMode=yes -o ConnectTimeout=5 "$DEST_USER@$DEST_HOST" "echo SSH key working" > /dev/null 2>&1

if [[ $? -ne 0 ]]; then
    log_message "INFO" "SSH key not installed on remote server. Please enter password to install it."
    ssh-copy-id -i "$SSH_KEY_PATH.pub" "$DEST_USER@$DEST_HOST"
    
    if [[ $? -ne 0 ]]; then
        log_message "ERROR" "Failed to install SSH key on remote server"
        exit 1
    fi
    
    log_message "SUCCESS" "SSH key installed successfully on remote server"
else
    log_message "INFO" "SSH key already working"
fi

# Create a timestamp for backup
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
BACKUP_NAME="openshot_backup_$TIMESTAMP"

# Create destination directory
log_message "INFO" "Creating backup directory on remote server..."
ssh "$DEST_USER@$DEST_HOST" "mkdir -p $DEST_DIR"

# Perform the backup using rsync
log_message "INFO" "Starting rsync backup..."
rsync -avz --delete --exclude='.git' \
      "$SOURCE_DIR" "$DEST_USER@$DEST_HOST:$DEST_DIR" \
      >> "$LOG_FILE" 2>&1

# Check the status of rsync
if [[ $? -eq 0 ]]; then
    log_message "SUCCESS" "Backup completed successfully to $DEST_USER@$DEST_HOST:$DEST_DIR"
else
    log_message "ERROR" "Backup failed. See $LOG_FILE for details"
    exit 1
fi

# Add a timestamp file to the remote server for versioning information
ssh "$DEST_USER@$DEST_HOST" "echo Backup completed on $(date) > $DEST_DIR/last_backup_$TIMESTAMP.txt"

log_message "INFO" "Backup process completed"

exit 0