#!/bin/bash
set -e

# Create data directories
mkdir -p /data/vms
mkdir -p /data/config

# Initialize TwinShare configuration
echo "Initializing TwinShare..."
twinshare --config /data/config/twinshare.conf --debug

# Start P2P services
echo "Starting P2P services..."
twinshare p2p start

# Wait for P2P services to initialize
sleep 5

# Check P2P status
echo "Checking P2P status..."
twinshare p2p status

# List P2P peers
echo "Listing P2P peers..."
twinshare p2p list || echo "No peers found yet, continuing..."

# If this is the server node, create a test VM
if [ "$TWINSHARE_NODE_TYPE" = "server" ]; then
    echo "Setting up server node..."
    
    # Start the REST API server
    echo "Starting REST API server..."
    twinshare api start --host 0.0.0.0 --port 37780 --daemon
    
    # Create a test VM if it doesn't exist
    echo "Checking for test VM..."
    if ! twinshare vm list | grep -q "test-vm"; then
        echo "Creating test VM..."
        # Use a minimal image to reduce resource requirements
        twinshare vm create test-vm --image alpine:latest --memory 256 --disk 1 || echo "Failed to create VM, but continuing..."
    fi
    
    # List VMs
    echo "Listing VMs on server..."
    twinshare vm list
fi

# If this is the client node, wait for server to be available and then try to access it
if [ "$TWINSHARE_NODE_TYPE" = "client" ]; then
    echo "Setting up client node..."
    
    # Wait for server to be discoverable
    echo "Waiting for server to be discoverable..."
    MAX_ATTEMPTS=30
    for i in $(seq 1 $MAX_ATTEMPTS); do
        if twinshare p2p list | grep -q "twinshare-server"; then
            echo "Server discovered!"
            break
        fi
        
        if [ $i -eq $MAX_ATTEMPTS ]; then
            echo "Warning: Could not discover server after $MAX_ATTEMPTS attempts"
        else
            echo "Waiting for server... (attempt $i/$MAX_ATTEMPTS)"
            sleep 2
        fi
    done
    
    # Try to list remote VMs
    echo "Listing remote VMs on server..."
    twinshare remote vm-list --peer twinshare-server || echo "Failed to list remote VMs by hostname"
    twinshare remote vm-list --peer 172.28.0.2 || echo "Failed to list remote VMs by IP"
fi

# Keep the container running
echo "TwinShare setup complete. Container is now running..."
tail -f /dev/null
