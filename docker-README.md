# TwinShare Docker Testing Environment

This Docker Compose setup creates a simulated environment with two TwinShare nodes to test P2P networking and VM sharing functionality.

## Overview

The setup consists of:
- **twinshare-server**: A TwinShare node that hosts VMs and serves as the P2P server
- **twinshare-client**: A TwinShare node that connects to the server and manages VMs remotely

Both containers are connected to the same network, allowing them to discover each other via the P2P discovery protocol.

## Prerequisites

- Docker
- Docker Compose

## Usage

### Starting the Environment

```bash
# Make the test script executable
chmod +x test-p2p.sh

# Run the test script
./test-p2p.sh
```

The test script will:
1. Create necessary data directories
2. Build and start the Docker containers
3. Wait for the containers to initialize
4. Check the P2P status on both server and client
5. Test remote VM operations from the client to the server

### Manual Testing

You can also interact with the containers manually:

```bash
# Check server status
docker exec twinshare-server twinshare p2p status

# List VMs on server
docker exec twinshare-server twinshare vm list

# List peers from client
docker exec twinshare-client twinshare p2p list

# List remote VMs from client
docker exec twinshare-client twinshare remote vm-list --peer twinshare-server
```

### Cleaning Up

```bash
# Stop and remove containers
docker-compose down
```

## Troubleshooting

If the client cannot discover the server:
1. Check that both containers are running: `docker-compose ps`
2. Verify network connectivity: `docker exec twinshare-client ping twinshare-server`
3. Check P2P services status: `docker exec twinshare-server twinshare p2p status`
4. Inspect logs: `docker-compose logs`

## Configuration

The Docker environment uses the following configuration:
- P2P Discovery Port: 37777/UDP
- P2P Network Port: 37778/TCP
- REST API Port: 37780/TCP
- Network: 172.28.0.0/16
  - Server IP: 172.28.0.2
  - Client IP: 172.28.0.3
