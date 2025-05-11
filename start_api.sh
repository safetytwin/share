#!/bin/bash
# Script to start the twinshare REST API service

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

# Create necessary directories
mkdir -p /tmp/twinshare/logs
mkdir -p /tmp/twinshare/run

# Set up environment variables
export PYTHONPATH="$PROJECT_DIR"

# Function to start the API
start_api() {
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
    fi
}

# Function to stop the API
stop_api() {
    print_message "Stopping twinshare REST API..."
    python3 "$PROJECT_DIR/scripts/start_rest_api.py" stop \
        --pid-file /tmp/twinshare/run/rest_api.pid
    
    if [ $? -eq 0 ]; then
        print_message "REST API stopped successfully!"
    else
        print_error "Failed to stop REST API"
    fi
}

# Function to check API status
status_api() {
    print_message "Checking twinshare REST API status..."
    
    if [ -f "/tmp/twinshare/run/rest_api.pid" ]; then
        PID=$(cat /tmp/twinshare/run/rest_api.pid)
        if ps -p $PID > /dev/null; then
            print_message "REST API is running with PID: $PID"
            print_message "API is available at: http://localhost:37780"
            return 0
        else
            print_warning "PID file exists but process is not running"
            print_message "You may need to remove the stale PID file:"
            print_message "rm /tmp/twinshare/run/rest_api.pid"
            return 1
        fi
    else
        print_message "REST API is not running"
        return 1
    fi
}

# Process command line arguments
case "$1" in
    start)
        start_api
        ;;
    stop)
        stop_api
        ;;
    restart)
        stop_api
        sleep 2
        start_api
        ;;
    status)
        status_api
        ;;
    *)
        print_message "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
