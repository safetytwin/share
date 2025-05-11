#!/bin/bash
# Script to test the twinshare REST API

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

# API base URL
API_URL="http://localhost:37780"

# Function to create a workspace
create_workspace() {
    local workspace_name=$1
    print_message "Creating workspace: $workspace_name"
    
    # Check if workspace exists
    response=$(curl -s -X GET "$API_URL/workspaces")
    if echo "$response" | grep -q "$workspace_name"; then
        print_message "Workspace '$workspace_name' already exists"
    else
        print_message "Creating new workspace..."
        response=$(curl -s -X POST "$API_URL/workspaces" \
            -H "Content-Type: application/json" \
            -d "{\"name\": \"$workspace_name\"}")
        
        if echo "$response" | grep -q "success"; then
            print_message "Workspace created successfully"
        else
            print_error "Failed to create workspace: $response"
            return 1
        fi
    fi
    return 0
}

# Function to share a workspace
share_workspace() {
    local workspace_name=$1
    local enable=$2
    
    print_message "Sharing workspace: $workspace_name (enable=$enable)"
    
    response=$(curl -s -X POST "$API_URL/shared/$workspace_name" \
        -H "Content-Type: application/json" \
        -d "{\"enable\": $enable}")
    
    if echo "$response" | grep -q "success"; then
        print_message "Workspace sharing updated successfully"
    else
        print_error "Failed to update workspace sharing: $response"
        return 1
    fi
    return 0
}

# Function to list shared workspaces
list_shared_workspaces() {
    print_message "Listing shared workspaces"
    
    response=$(curl -s -X GET "$API_URL/shared")
    echo "$response" | python3 -m json.tool
}

# Function to check API status
check_api_status() {
    print_message "Checking API status"
    
    response=$(curl -s -X GET "$API_URL/status")
    if [ $? -eq 0 ]; then
        echo "$response" | python3 -m json.tool
    else
        print_error "API is not responding"
        return 1
    fi
    return 0
}

# Function to list all workspaces
list_workspaces() {
    print_message "Listing all workspaces"
    
    response=$(curl -s -X GET "$API_URL/workspaces")
    echo "$response" | python3 -m json.tool
}

# Function to run a complete test
run_test() {
    local workspace_name="test_workspace"
    
    print_message "Running complete API test"
    
    # Check API status
    check_api_status || return 1
    
    # List workspaces
    list_workspaces
    
    # Create workspace
    create_workspace "$workspace_name" || return 1
    
    # Share workspace
    share_workspace "$workspace_name" true || return 1
    
    # List shared workspaces
    list_shared_workspaces
    
    # Unshare workspace
    share_workspace "$workspace_name" false || return 1
    
    print_message "API test completed successfully"
    return 0
}

# Process command line arguments
case "$1" in
    status)
        check_api_status
        ;;
    list)
        list_workspaces
        ;;
    create)
        if [ -z "$2" ]; then
            print_error "Workspace name is required"
            echo "Usage: $0 create <workspace_name>"
            exit 1
        fi
        create_workspace "$2"
        ;;
    share)
        if [ -z "$2" ]; then
            print_error "Workspace name is required"
            echo "Usage: $0 share <workspace_name> [true|false]"
            exit 1
        fi
        enable="true"
        if [ "$3" == "false" ]; then
            enable="false"
        fi
        share_workspace "$2" "$enable"
        ;;
    shared)
        list_shared_workspaces
        ;;
    test)
        run_test
        ;;
    *)
        print_message "Usage: $0 {status|list|create|share|shared|test}"
        print_message "  status - Check API status"
        print_message "  list - List all workspaces"
        print_message "  create <workspace_name> - Create a new workspace"
        print_message "  share <workspace_name> [true|false] - Share/unshare a workspace"
        print_message "  shared - List shared workspaces"
        print_message "  test - Run a complete API test"
        exit 1
        ;;
esac

exit 0
