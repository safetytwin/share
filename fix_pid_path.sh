#!/bin/bash
# Script to fix the PID file path issues for twinshare REST API service

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${GREEN}[twinshare]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Get current username
CURRENT_USER=$(whoami)
print_message "Running as user: $CURRENT_USER"

# Get project directory
PROJECT_DIR=$(pwd)
print_message "Project directory: $PROJECT_DIR"

# Create necessary directories with proper permissions
print_message "Creating necessary directories with proper permissions..."
sudo mkdir -p /var/log/twinshare /run/twinshare
sudo chmod 755 /var/log/twinshare /run/twinshare
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/twinshare /run/twinshare

# Create a temporary service file with the current user and absolute paths
print_message "Creating customized service file..."
cat > /tmp/twinshare-rest-api.service << EOF
[Unit]
Description=twinshare REST API Server
After=network.target

[Service]
Type=forking
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PYTHONPATH=$PROJECT_DIR"
ExecStartPre=/bin/mkdir -p /var/log/twinshare /run/twinshare
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/scripts/start_rest_api.py start --log-file /var/log/twinshare/rest_api.log --pid-file /run/twinshare/rest_api.pid
ExecStop=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/scripts/start_rest_api.py stop --pid-file /run/twinshare/rest_api.pid
PIDFile=/run/twinshare/rest_api.pid
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Copy the updated service file to systemd
print_message "Installing service file to systemd..."
sudo cp /tmp/twinshare-rest-api.service /etc/systemd/system/
rm /tmp/twinshare-rest-api.service

# Reload systemd to apply changes
print_message "Reloading systemd configuration..."
sudo systemctl daemon-reload

# Stop the service if it's running
print_message "Stopping the service if it's running..."
sudo systemctl stop twinshare-rest-api

# Start the service
print_message "Starting the twinshare REST API service..."
sudo systemctl start twinshare-rest-api
status=$?

# Wait a bit for the service to start
sleep 5

# Check service status
print_message "Checking service status..."
sudo systemctl status twinshare-rest-api

if [ $status -ne 0 ]; then
    print_error "Failed to start the service. Checking logs..."
    sudo journalctl -u twinshare-rest-api -n 20
    exit 1
fi

print_message "Service fix complete!"
print_message "You can check its status anytime with: sudo systemctl status twinshare-rest-api"
print_message "To stop the service: sudo systemctl stop twinshare-rest-api"
print_message "To restart the service: sudo systemctl restart twinshare-rest-api"
print_message "To view logs: sudo journalctl -u twinshare-rest-api"
