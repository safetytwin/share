# P2P Networking in TwinShare

This document describes the peer-to-peer (P2P) networking functionality in TwinShare, which enables communication between nodes for remote VM and container management.

## Overview

TwinShare uses a custom P2P protocol to discover and communicate with other nodes in the network. This allows users to:

- Discover other TwinShare nodes on the local network
- Manage VMs and containers on remote nodes
- Transfer files between nodes
- Execute commands remotely

## Architecture

The P2P networking functionality consists of two main components:

1. **P2P Discovery Service**: Responsible for discovering and tracking peers in the network
2. **P2P Network Service**: Handles communication between peers

### P2P Discovery Service

The discovery service broadcasts the node's presence on the network and listens for broadcasts from other nodes. It maintains a list of known peers and their capabilities.

Key features:
- Node identification using unique peer IDs
- Automatic peer discovery via UDP broadcasts
- Support for looking up peers by hostname or IP address
- Tracking of peer capabilities and resources

### P2P Network Service

The network service provides a secure communication channel between peers. It handles message routing, serialization, and error handling.

Key features:
- Message-based communication protocol
- Support for various message types (VM operations, container operations, etc.)
- Secure communication using SSL/TLS
- Special handling for local connections (localhost and local IP addresses)

## Usage

### Starting and Stopping P2P Services

```bash
# Start P2P services
twinshare p2p start

# Stop P2P services
twinshare p2p stop

# Check the status of P2P services
twinshare p2p status
```

The `status` command will show whether the P2P discovery and network services are currently running or stopped.

### Listing Peers

```bash
# List peers
twinshare p2p list
```

### Remote VM Management

```bash
# List VMs on a remote peer
twinshare remote vm-list --peer <peer_id_or_hostname_or_ip>

# Create a VM on a remote peer
twinshare remote vm-create --peer <peer_id_or_hostname_or_ip> --name <vm_name> --image <image> --memory <memory_mb> --disk <disk_gb>

# Start a VM on a remote peer
twinshare remote vm-start --peer <peer_id_or_hostname_or_ip> --name <vm_name>

# Stop a VM on a remote peer
twinshare remote vm-stop --peer <peer_id_or_hostname_or_ip> --name <vm_name>

# Delete a VM on a remote peer
twinshare remote vm-delete --peer <peer_id_or_hostname_or_ip> --name <vm_name>
```

## Configuration

The P2P networking functionality can be configured in the TwinShare configuration file:

```yaml
p2p:
  discovery:
    port: 37777
    broadcast_interval: 60
    peer_timeout: 300
  network:
    port: 37778
    ssl_enabled: true
    max_connections: 100
```

## Troubleshooting

### Common Issues

#### Cannot discover peers
- Ensure that the P2P discovery service is running (`twinshare p2p status`)
- Check if UDP broadcasts are allowed on your network
- Verify that the discovery port (default: 37777) is not blocked by a firewall

#### Cannot connect to peers
- Ensure that the P2P network service is running
- Check if the peer is reachable (using ping or similar tools)
- Verify that the network port (default: 37778) is not blocked by a firewall

#### Connection errors
- Check SSL/TLS configuration if secure communication is enabled
- Ensure that the peer ID is correct
- Verify that the peer is still active and available

## Advanced Topics

### Custom Message Handlers

The P2P network service can be extended with custom message handlers to support additional functionality. This is done by registering handlers for specific message types.

### Security Considerations

- All communication between peers should be encrypted using SSL/TLS
- Authentication mechanisms should be implemented to verify peer identity
- Access control should be implemented to restrict operations on remote nodes
