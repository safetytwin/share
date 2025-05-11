#!/bin/bash
# twinshare REST API Service Starter
# This script installs and starts the REST API service

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

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURRENT_USER=$(whoami)

# Check if running with sudo privileges
if ! sudo -n true 2>/dev/null; then
    print_warning "This script requires sudo privileges to install and start the service."
    print_message "You will be prompted for your password."
    sudo true || { print_error "Failed to obtain sudo privileges. Exiting."; exit 1; }
fi

print_message "Installing and starting the REST API service..."

# Ensure required Python packages are installed in the virtual environment
if [ -d "$PROJECT_DIR/venv" ]; then
    print_message "Ensuring required Python packages are installed..."
    "$PROJECT_DIR/venv/bin/pip" install python-daemon
    "$PROJECT_DIR/venv/bin/pip" install "aiohttp[speedups]<4.0.0,>=3.8.0"
    "$PROJECT_DIR/venv/bin/pip" install aiohttp-cors>=0.7.0
else
    print_warning "Virtual environment not found at $PROJECT_DIR/venv"
    print_message "Creating virtual environment and installing dependencies..."
    python3 -m venv "$PROJECT_DIR/venv"
    "$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
fi

# Create required directories
print_message "Creating required directories..."
sudo mkdir -p /var/log/twinshare /var/run/twinshare
sudo chown $CURRENT_USER:$CURRENT_USER /var/log/twinshare /var/run/twinshare
print_message "Directories created and permissions set."

# Copy and customize service file
if [ -f "$PROJECT_DIR/scripts/twinshare-rest-api.service" ]; then
    print_message "Customizing service file for user $CURRENT_USER..."
    # Create a temporary service file with the current user and absolute paths
    cat "$PROJECT_DIR/scripts/twinshare-rest-api.service" | \
        sed "s/\$USER/$CURRENT_USER/g" | \
        sed "s|/home/tom/github/twinshare/share|$PROJECT_DIR|g" | \
        sed "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_DIR|g" | \
        sed "s|Environment=.*|Environment=\"PYTHONPATH=$PROJECT_DIR\"|g" | \
        sed "s|/home/tom/github/twinshare/share/venv/bin/python3|$PROJECT_DIR/venv/bin/python3|g" > /tmp/twinshare-rest-api.service
    
    sudo cp /tmp/twinshare-rest-api.service /etc/systemd/system/twinshare-rest-api.service
    rm /tmp/twinshare-rest-api.service
    print_message "Service file copied to system directory."
else
    print_error "Service file not found at $PROJECT_DIR/scripts/twinshare-rest-api.service"
    exit 1
fi

# Reload systemd
sudo systemctl daemon-reload
print_message "Systemd configuration reloaded."

# Enable and start the service
sudo systemctl enable twinshare-rest-api
print_message "Service enabled to start on boot."

sudo systemctl start twinshare-rest-api
status=$?
if [ $status -ne 0 ]; then
    print_error "Failed to start the service. Checking logs..."
    sudo journalctl -u twinshare-rest-api -n 20
    exit 1
fi

# Check service status
print_message "Checking service status..."
sudo systemctl status twinshare-rest-api

print_message "REST API service installation complete!"
print_message "You can check its status anytime with: sudo systemctl status twinshare-rest-api"
print_message "To stop the service: sudo systemctl stop twinshare-rest-api"
print_message "To restart the service: sudo systemctl restart twinshare-rest-api"
print_message "To view logs: sudo journalctl -u twinshare-rest-api"
