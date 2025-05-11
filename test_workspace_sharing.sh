#!/bin/bash
# Script to test the workspace sharing functionality

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

# Function to test CLI command
test_cli_command() {
    print_message "Testing CLI command: $1"
    export PYTHONPATH="$PROJECT_DIR"
    python3 -m src.cli.main $1
    if [ $? -eq 0 ]; then
        print_message "Command executed successfully"
    else
        print_error "Command failed"
    fi
}

# Function to test API endpoint
test_api_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    print_message "Testing API endpoint: $method $endpoint"
    
    if [ -n "$data" ]; then
        curl -s -X $method "http://localhost:37780$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" | python3 -m json.tool
    else
        curl -s -X $method "http://localhost:37780$endpoint" | python3 -m json.tool
    fi
}

# Function to run a background process
run_background() {
    print_message "Starting $1 in background"
    $@ > /tmp/twinshare/logs/background.log 2>&1 &
    echo $! > /tmp/twinshare/run/background.pid
    print_message "Process started with PID $(cat /tmp/twinshare/run/background.pid)"
    print_message "Log file: /tmp/twinshare/logs/background.log"
}

# Function to stop a background process
stop_background() {
    if [ -f "/tmp/twinshare/run/background.pid" ]; then
        PID=$(cat /tmp/twinshare/run/background.pid)
        print_message "Stopping process with PID: $PID"
        kill $PID 2>/dev/null
        rm -f /tmp/twinshare/run/background.pid
    else
        print_warning "No background process found"
    fi
}

# Create necessary directories
mkdir -p /tmp/twinshare/logs
mkdir -p /tmp/twinshare/run

# Process command line arguments
case "$1" in
    start-api)
        # Start the simple API server in the background
        run_background python3 "$PROJECT_DIR/simple_api_server.py"
        sleep 2
        print_message "Testing API connection..."
        curl -s http://localhost:37780/
        ;;
    stop-api)
        # Stop the background API server
        stop_background
        ;;
    test-api)
        # Test the API endpoints
        print_message "Testing API endpoints"
        test_api_endpoint "GET" "/"
        test_api_endpoint "GET" "/shared"
        test_api_endpoint "POST" "/shared/my_workspace" '{"enable": true}'
        test_api_endpoint "DELETE" "/shared/my_workspace"
        ;;
    test-cli)
        # Test the CLI commands
        print_message "Testing CLI commands"
        test_cli_command "workspace list"
        test_cli_command "workspace share --name my_workspace"
        test_cli_command "workspace unshare --name my_workspace"
        ;;
    *)
        print_message "Usage: $0 {start-api|stop-api|test-api|test-cli}"
        print_message "  start-api - Start the API server in background"
        print_message "  stop-api - Stop the background API server"
        print_message "  test-api - Test the API endpoints"
        print_message "  test-cli - Test the CLI commands"
        exit 1
        ;;
esac

exit 0
