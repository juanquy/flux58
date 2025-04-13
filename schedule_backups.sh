#!/bin/bash

# Script to set up automated backups using cron
# This will configure cron to run the backup_openshot.sh script every 15 minutes

# Configuration
BACKUP_SCRIPT="/home/juanquy/OpenShot/backup_openshot.sh"
CRON_SCHEDULE="*/15 * * * *"
CRON_USER=$(whoami)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check if backup script exists
if [[ ! -f "$BACKUP_SCRIPT" ]]; then
    echo -e "${RED}[ERROR]${NC} Backup script not found at $BACKUP_SCRIPT"
    exit 1
fi

# Check if backup script is executable
if [[ ! -x "$BACKUP_SCRIPT" ]]; then
    echo -e "${YELLOW}[INFO]${NC} Making backup script executable"
    chmod +x "$BACKUP_SCRIPT"
fi

# Create temporary cron file
TEMP_CRON=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# New crontab" > "$TEMP_CRON"

# Check if entry already exists
if grep -q "$BACKUP_SCRIPT" "$TEMP_CRON"; then
    echo -e "${YELLOW}[INFO]${NC} Backup job already exists in crontab. Updating..."
    # Remove existing entry
    sed -i "\|$BACKUP_SCRIPT|d" "$TEMP_CRON"
fi

# Add new cron job
echo "$CRON_SCHEDULE $BACKUP_SCRIPT" >> "$TEMP_CRON"

# Install new crontab
crontab "$TEMP_CRON"

# Cleanup
rm "$TEMP_CRON"

echo -e "${GREEN}[SUCCESS]${NC} Automated backup scheduled every 15 minutes!"
echo -e "Use ${YELLOW}crontab -l${NC} to view the scheduled jobs"
echo -e "Use ${YELLOW}$BACKUP_SCRIPT${NC} to run a backup manually"

# Show next execution times
echo 
echo -e "${YELLOW}[INFO]${NC} Next 3 scheduled backup times:"
current_time=$(date +%s)
for i in {1..3}; do
    # Calculate next execution time
    # This is a simplification - actual cron scheduling is more complex
    minutes_to_add=$(( (15 - ($(date +%M) % 15)) % 15 ))
    if [[ $minutes_to_add -eq 0 ]]; then
        minutes_to_add=15
    fi
    
    next_time=$((current_time + minutes_to_add*60 + (i-1)*15*60))
    echo "  $(date -d @$next_time "+%Y-%m-%d %H:%M:%S")"
    
    if [[ $i -eq 1 ]]; then
        current_time=$next_time
    fi
done

echo
echo -e "${YELLOW}[INFO]${NC} Logs will be saved to: /home/juanquy/openshot_backup.log"

exit 0