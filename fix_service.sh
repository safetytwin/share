#!/bin/bash
# Script to fix the SafetyTwin REST API service

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

# Check if running with sudo privileges
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (with sudo)."
    exit 1
fi

print_message "Restarting the SafetyTwin REST API service..."

# Restart the service
systemctl restart safetytwin-rest-api
status=$?

if [ $status -ne 0 ]; then
    print_error "Failed to start the service. Checking logs..."
    journalctl -u safetytwin-rest-api -n 20
    exit 1
fi

# Check service status
print_message "Checking service status..."
systemctl status safetytwin-rest-api

print_message "Service fix complete!"
print_message "You can check its status anytime with: sudo systemctl status safetytwin-rest-api"
print_message "To stop the service: sudo systemctl stop safetytwin-rest-api"
print_message "To restart the service: sudo systemctl restart safetytwin-rest-api"
print_message "To view logs: sudo journalctl -u safetytwin-rest-api"
