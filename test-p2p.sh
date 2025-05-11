#!/bin/bash
set -e

echo "=== TwinShare P2P Testing Script ==="
echo "This script will test the P2P functionality between two Docker containers"
echo ""

# Make sure Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed."
    exit 1
fi

# Create data directories
mkdir -p data/server
mkdir -p data/client

# Make the entrypoint script executable
chmod +x docker-entrypoint.sh

# Clean up any existing containers
echo "Cleaning up any existing containers..."
docker-compose down -v 2>/dev/null || true

# Build and start the containers
echo "Building and starting containers..."
docker-compose up -d --build

# Function to check if containers are running
check_containers() {
    if [ "$(docker ps -q -f name=twinshare-server)" ] && [ "$(docker ps -q -f name=twinshare-client)" ]; then
        return 0
    else
        return 1
    fi
}

# Wait for containers to start
echo "Waiting for containers to start..."
TIMEOUT=30
for i in $(seq 1 $TIMEOUT); do
    if check_containers; then
        echo "Both containers are running!"
        break
    fi
    
    if [ $i -eq $TIMEOUT ]; then
        echo "Error: Containers failed to start within $TIMEOUT seconds."
        docker-compose logs
        exit 1
    fi
    
    echo "Waiting for containers to start... ($i/$TIMEOUT)"
    sleep 1
done

# Wait for initialization
echo "Waiting for containers to initialize (45 seconds)..."
sleep 45

echo ""
echo "=== Server Status ==="
docker exec twinshare-server twinshare p2p status || echo "Failed to get P2P status on server"
docker exec twinshare-server twinshare vm list || echo "Failed to list VMs on server"

echo ""
echo "=== Client Status ==="
docker exec twinshare-client twinshare p2p status || echo "Failed to get P2P status on client"
docker exec twinshare-client twinshare p2p list || echo "Failed to list peers on client"

echo ""
echo "=== Testing Remote VM Operations ==="
echo "1. Listing remote VMs from client..."
docker exec twinshare-client twinshare remote vm-list --peer twinshare-server || echo "Failed to list remote VMs by hostname"
docker exec twinshare-client twinshare remote vm-list --peer 172.28.0.2 || echo "Failed to list remote VMs by IP"

echo ""
echo "2. Starting test-vm on server from client..."
docker exec twinshare-client twinshare remote vm-start --peer twinshare-server --name test-vm || echo "Failed to start remote VM"

echo ""
echo "3. Checking VM status from client..."
docker exec twinshare-client twinshare remote vm-list --peer twinshare-server || echo "Failed to list remote VMs"

echo ""
echo "4. Stopping test-vm on server from client..."
docker exec twinshare-client twinshare remote vm-stop --peer twinshare-server --name test-vm || echo "Failed to stop remote VM"

echo ""
echo "5. Final VM status check from client..."
docker exec twinshare-client twinshare remote vm-list --peer twinshare-server || echo "Failed to list remote VMs"

echo ""
echo "=== Test Complete ==="
echo "To view logs, run: docker-compose logs"
echo "To clean up, run: docker-compose down"
