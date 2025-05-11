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
echo "Waiting for containers to initialize (30 seconds)..."
sleep 30

echo ""
echo "=== Server P2P Status ==="
docker exec twinshare-server twinshare p2p status || echo "Failed to get P2P status on server"

echo ""
echo "=== Client P2P Status ==="
docker exec twinshare-client twinshare p2p status || echo "Failed to get P2P status on client"

echo ""
echo "=== P2P Peer Discovery ==="
echo "1. Listing peers from server..."
docker exec twinshare-server twinshare p2p list || echo "Failed to list peers from server"

echo ""
echo "2. Listing peers from client..."
docker exec twinshare-client twinshare p2p list || echo "Failed to list peers from client"

echo ""
echo "=== P2P Communication Test ==="
echo "1. Pinging server from client by hostname..."
docker exec twinshare-client twinshare p2p ping --peer twinshare-server || echo "Failed to ping server by hostname"

echo ""
echo "2. Pinging server from client by IP..."
docker exec twinshare-client twinshare p2p ping --peer 172.28.0.2 || echo "Failed to ping server by IP"

echo ""
echo "=== Test Complete ==="
echo "To view logs, run: docker-compose logs"
echo "To clean up, run: docker-compose down"
