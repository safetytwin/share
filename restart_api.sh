#!/bin/bash
# Script to restart the twinshare REST API service

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

# Get project directory
PROJECT_DIR=$(pwd)
print_message "Project directory: $PROJECT_DIR"

# Stop any running API processes
print_message "Stopping any running API processes..."

# Find and kill all running API processes
API_PIDS=$(ps aux | grep -i "start_rest_api.py" | grep -v grep | awk '{print $2}')
if [ -n "$API_PIDS" ]; then
    for PID in $API_PIDS; do
        print_message "Stopping process with PID: $PID"
        kill $PID 2>/dev/null
    done
    sleep 2
    
    # Check if processes are still running
    STILL_RUNNING=$(ps aux | grep -i "start_rest_api.py" | grep -v grep | awk '{print $2}')
    if [ -n "$STILL_RUNNING" ]; then
        print_warning "Some processes are still running. Forcing termination..."
        for PID in $STILL_RUNNING; do
            print_message "Force stopping process with PID: $PID"
            kill -9 $PID 2>/dev/null
        done
    fi
else
    print_message "No API processes found running"
fi

# Clean up any stale PID files
if [ -f "/tmp/twinshare/run/rest_api.pid" ]; then
    print_message "Removing stale PID file"
    rm -f /tmp/twinshare/run/rest_api.pid
fi

# Create necessary directories
mkdir -p /tmp/twinshare/logs
mkdir -p /tmp/twinshare/run

# Set up environment variables
export PYTHONPATH="$PROJECT_DIR"

# Start the API
print_message "Starting twinshare REST API..."
python3 "$PROJECT_DIR/scripts/start_rest_api.py" start \
    --host 0.0.0.0 \
    --port 37780 \
    --log-file /tmp/twinshare/logs/rest_api.log \
    --pid-file /tmp/twinshare/run/rest_api.pid

if [ $? -eq 0 ]; then
    print_message "REST API started successfully!"
    print_message "API is available at: http://localhost:37780"
    print_message "Log file: /tmp/twinshare/logs/rest_api.log"
    print_message "PID file: /tmp/twinshare/run/rest_api.pid"
else
    print_error "Failed to start REST API"
    exit 1
fi

# Wait a moment for the API to initialize
sleep 2

# Test the API
print_message "Testing API connection..."
RESPONSE=$(curl -s http://localhost:37780/)
if [ $? -eq 0 ]; then
    print_message "API is responding!"
    echo "$RESPONSE"
else
    print_error "API is not responding"
    exit 1
fi

print_message "API restart completed successfully"
exit 0
