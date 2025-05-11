#!/bin/bash
set -e

# Create data directories
mkdir -p /data/config

echo "=== TwinShare P2P Test Environment ==="

# Initialize configuration
echo "Initializing configuration..."
mkdir -p /root/.ai-environment
cat > /root/.ai-environment/config.yaml << EOF
p2p:
  discovery_port: 37777
  network_port: 37778
  node_id: "$(hostname)-$(date +%s)"
  capabilities:
    - "p2p"
EOF

# Start P2P services
echo "Starting P2P discovery service..."
twinshare p2p start-discovery

echo "Starting P2P network service..."
twinshare p2p start-network

# Wait for P2P services to initialize
sleep 5

# Check P2P status
echo "Checking P2P status..."
twinshare p2p status || echo "Failed to get P2P status"

# List P2P peers
echo "Listing P2P peers..."
twinshare p2p list || echo "No peers found yet, continuing..."

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
    
    # Try to ping the server
    echo "Pinging server..."
    twinshare p2p ping --peer twinshare-server || echo "Failed to ping server by hostname"
    twinshare p2p ping --peer 172.28.0.2 || echo "Failed to ping server by IP"
fi

# Keep the container running
echo "TwinShare P2P setup complete. Container is now running..."
tail -f /dev/null
