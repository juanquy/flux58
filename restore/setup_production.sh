#!/bin/bash

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "/home/juanquy/openshot_service_venv" ]; then
    python3 -m venv /home/juanquy/openshot_service_venv
fi

# Install gunicorn in virtual environment
. /home/juanquy/openshot_service_venv/bin/activate
pip install gunicorn

# Create systemd service file
cat > openshot-web.service << 'EOL'
[Unit]
Description=OpenShot Web Service
After=network.target postgresql.service

[Service]
User=juanquy
WorkingDirectory=/home/juanquy/OpenShot/test_app
ExecStart=/home/juanquy/openshot_service_venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
Restart=on-failure
Environment="FLASK_ENV=production"

[Install]
WantedBy=multi-user.target
EOL

# Update .env file content for production
cat > env_production << 'EOL'
# Database Configuration
DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=flux58
DB_USER=flux58_user
DB_PASS=flux58_password

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
FLASK_APP=app.py

# Application Settings
LOG_LEVEL=INFO
EXPORT_CONCURRENT_JOBS=2
EOL

echo "========================================"
echo "Production setup files have been created"
echo "========================================"
echo ""
echo "To complete setup, run the following commands with sudo:"
echo ""
echo "  # Install systemd service"
echo "  sudo mv openshot-web.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable openshot-web.service"
echo ""
echo "  # Replace .env file with production settings"
echo "  sudo cp env_production /home/juanquy/OpenShot/test_app/.env"
echo ""
echo "  # Set proper file permissions"
echo "  sudo chown -R juanquy:juanquy /home/juanquy/OpenShot/test_app"
echo "  sudo chmod -R 755 /home/juanquy/OpenShot/test_app"
echo "  sudo chmod 640 /home/juanquy/OpenShot/test_app/.env"
echo ""
echo "  # Start the service"
echo "  sudo systemctl start openshot-web.service"
echo ""
echo "  # Check status"
echo "  sudo systemctl status openshot-web.service"
