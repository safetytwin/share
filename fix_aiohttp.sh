#!/bin/bash
# Script to fix aiohttp version and restart the service

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

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

print_message "Fixing aiohttp version issue..."

# Activate virtual environment and install correct aiohttp version
source "$PROJECT_DIR/venv/bin/activate"
pip install "aiohttp[speedups]<4.0.0,>=3.8.0" aiohttp-cors>=0.7.0
deactivate

print_message "Dependencies installed successfully."
print_message "Now you can restart the service with:"
echo "sudo systemctl restart safetytwin-rest-api"
print_message "And check its status with:"
echo "sudo systemctl status safetytwin-rest-api"
