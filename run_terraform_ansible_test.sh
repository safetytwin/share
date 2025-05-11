#!/bin/bash
set -e

echo "=== TwinShare P2P Testing with Terraform and Ansible ==="
echo "This script will set up a test environment and run P2P tests using Terraform and Ansible"
echo ""

# Check for required tools
if ! command -v terraform &> /dev/null; then
    echo "Error: terraform is not installed."
    echo "Please install Terraform: https://developer.hashicorp.com/terraform/install"
    exit 1
fi

if ! command -v ansible &> /dev/null; then
    echo "Error: ansible is not installed."
    echo "Please install Ansible: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html"
    exit 1
fi

# Check for port conflicts
echo "Checking for port conflicts..."
PORT_47777_IN_USE=$(netstat -tuln | grep ":47777" || true)
PORT_47778_IN_USE=$(netstat -tuln | grep ":47778" || true)

if [ ! -z "$PORT_47777_IN_USE" ] || [ ! -z "$PORT_47778_IN_USE" ]; then
    echo "Warning: One or more required ports are already in use:"
    [ ! -z "$PORT_47777_IN_USE" ] && echo "  - Port 47777: $PORT_47777_IN_USE"
    [ ! -z "$PORT_47778_IN_USE" ] && echo "  - Port 47778: $PORT_47778_IN_USE"
    
    echo "Attempting to identify and stop conflicting processes..."
    
    if [ ! -z "$PORT_47777_IN_USE" ]; then
        PID_47777=$(lsof -i:47777 -t 2>/dev/null || true)
        if [ ! -z "$PID_47777" ]; then
            echo "  Process using port 47777: $(ps -p $PID_47777 -o comm=)"
            echo "  Stopping process $PID_47777..."
            kill -15 $PID_47777 2>/dev/null || true
        fi
    fi
    
    if [ ! -z "$PORT_47778_IN_USE" ]; then
        PID_47778=$(lsof -i:47778 -t 2>/dev/null || true)
        if [ ! -z "$PID_47778" ]; then
            echo "  Process using port 47778: $(ps -p $PID_47778 -o comm=)"
            echo "  Stopping process $PID_47778..."
            kill -15 $PID_47778 2>/dev/null || true
        fi
    fi
    
    # Wait a moment for processes to stop
    sleep 2
    
    # Check again
    PORT_47777_IN_USE=$(netstat -tuln | grep ":47777" || true)
    PORT_47778_IN_USE=$(netstat -tuln | grep ":47778" || true)
    
    if [ ! -z "$PORT_47777_IN_USE" ] || [ ! -z "$PORT_47778_IN_USE" ]; then
        echo "Error: Could not free the required ports. Please manually stop the processes using ports 47777 and 47778."
        exit 1
    else
        echo "Successfully freed the required ports."
    fi
fi

# Clean up any existing Docker resources
echo "Cleaning up any existing infrastructure..."
cd terraform
terraform destroy -auto-approve || true

# Also clean up any existing Docker resources that might conflict
echo "Cleaning up any existing Docker resources..."
docker rm -f twinshare-server twinshare-client 2>/dev/null || true
docker network rm p2p_test_network 2>/dev/null || true

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Apply Terraform configuration
echo "Applying Terraform configuration..."
terraform apply -auto-approve

# Check if Terraform apply was successful
if [ $? -ne 0 ]; then
    echo "Error: Terraform apply failed. Check the error messages above."
    exit 1
fi

# Wait for containers to initialize
echo "Waiting for containers to initialize (10 seconds)..."
sleep 10

# Check if containers are running
echo "Checking if containers are running..."
SERVER_RUNNING=$(docker ps -q -f name=twinshare-server)
CLIENT_RUNNING=$(docker ps -q -f name=twinshare-client)

if [ -z "$SERVER_RUNNING" ] || [ -z "$CLIENT_RUNNING" ]; then
    echo "Error: One or more containers are not running."
    echo "Server container: $(docker ps -a -f name=twinshare-server --format '{{.Status}}')"
    echo "Client container: $(docker ps -a -f name=twinshare-client --format '{{.Status}}')"
    echo "Check Docker logs for more information:"
    echo "  docker logs twinshare-server"
    echo "  docker logs twinshare-client"
    exit 1
fi

# Run Ansible playbook
echo "Running Ansible playbook..."
cd ../ansible
ansible-playbook -i inventory.yml playbook.yml

# Check if Ansible playbook was successful
if [ $? -ne 0 ]; then
    echo "Error: Ansible playbook failed. Check the error messages above."
    exit 1
fi

echo ""
echo "=== Test Complete ==="
echo "To view container logs, run: docker logs twinshare-server"
echo "                        or: docker logs twinshare-client"
echo "To clean up, run: cd terraform && terraform destroy -auto-approve"
