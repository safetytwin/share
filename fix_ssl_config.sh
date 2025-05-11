#!/bin/bash
# Script to fix the SSL configuration and PID file issues for SafetyTwin REST API service

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${GREEN}[SafetyTwin]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Create necessary directories with proper permissions
print_message "Creating necessary directories with proper permissions..."
sudo mkdir -p /run/safetytwin
sudo chmod 755 /run/safetytwin
sudo chown $(whoami):$(whoami) /run/safetytwin

# Update the service file to use /run instead of /var/run
print_message "Updating service file to use correct PID file path..."
sudo sed -i 's|/var/run/safetytwin|/run/safetytwin|g' /etc/systemd/system/safetytwin-rest-api.service

# Reload systemd to apply changes
print_message "Reloading systemd configuration..."
sudo systemctl daemon-reload

# Stop the service if it's running
print_message "Stopping the service if it's running..."
sudo systemctl stop safetytwin-rest-api

# Start the service
print_message "Starting the SafetyTwin REST API service..."
sudo systemctl start safetytwin-rest-api
status=$?

if [ $status -ne 0 ]; then
    print_error "Failed to start the service. Checking logs..."
    sudo journalctl -u safetytwin-rest-api -n 20
    exit 1
fi

# Check service status
print_message "Checking service status..."
sudo systemctl status safetytwin-rest-api

print_message "Service fix complete!"
print_message "You can check its status anytime with: sudo systemctl status safetytwin-rest-api"
print_message "To stop the service: sudo systemctl stop safetytwin-rest-api"
print_message "To restart the service: sudo systemctl restart safetytwin-rest-api"
print_message "To view logs: sudo journalctl -u safetytwin-rest-api"
