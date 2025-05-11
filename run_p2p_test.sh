#!/bin/bash
set -e

echo "=== TwinShare P2P Networking Test ==="
echo "This script will test the P2P networking functionality between two Docker containers"
echo ""

# Make sure Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed."
    exit 1
fi

# Clean up any existing containers
echo "Cleaning up any existing containers..."
docker-compose -f docker-compose.p2ptest.yml down -v 2>/dev/null || true

# Build and start the containers
echo "Building and starting containers..."
docker-compose -f docker-compose.p2ptest.yml up -d --build

# Function to check if containers are running
check_containers() {
    if [ "$(docker ps -q -f name=p2p-server)" ] && [ "$(docker ps -q -f name=p2p-client)" ]; then
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
        docker-compose -f docker-compose.p2ptest.yml logs
        exit 1
    fi
    
    echo "Waiting for containers to start... ($i/$TIMEOUT)"
    sleep 1
done

# Wait for initialization
echo "Waiting for initialization (10 seconds)..."
sleep 10

# Show logs
echo ""
echo "=== Server Logs ==="
docker logs p2p-server

echo ""
echo "=== Client Logs ==="
docker logs p2p-client

echo ""
echo "=== Test Complete ==="
echo "To view logs, run: docker-compose -f docker-compose.p2ptest.yml logs"
echo "To clean up, run: docker-compose -f docker-compose.p2ptest.yml down"
