# twinshare REST API Guide

This document provides comprehensive documentation for the twinshare REST API, which allows you to manage virtual machines, P2P networking, and remote VM management through HTTP requests.

**Last Updated:** May 11, 2025

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
   - [VM Management](#vm-management)
   - [P2P Networking](#p2p-networking)
   - [Remote VM Management](#remote-vm-management)
5. [Error Handling](#error-handling)
6. [Examples](#examples)
7. [Client Libraries](#client-libraries)
8. [Rate Limiting](#rate-limiting)
9. [Versioning](#versioning)

## Introduction

The twinshare REST API provides a programmatic interface to the AI Environment Manager, allowing you to:

- Create, manage, and monitor virtual machines
- Control P2P networking services
- Manage VMs on remote nodes in the P2P network
- Integrate with web applications and other services

The API uses standard HTTP methods and returns JSON responses. All API endpoints are prefixed with `/api`.

## Getting Started

### Starting the REST API Server

The REST API server can be started using the provided script:

```bash
# Start the server in the foreground
python3 scripts/start_rest_api.py start --foreground

# Start the server as a daemon
python3 scripts/start_rest_api.py start

# Check the server status
python3 scripts/start_rest_api.py status

# Stop the server
python3 scripts/start_rest_api.py stop

# Restart the server
python3 scripts/start_rest_api.py restart
```

Additional options:
```bash
# Specify host and port
python3 scripts/start_rest_api.py start --host 127.0.0.1 --port 8888

# Enable debug logging
python3 scripts/start_rest_api.py start --debug

# Specify custom log file location
python3 scripts/start_rest_api.py start --log-file /path/to/custom/log.log
```

### Installing as a System Service

You can install the REST API server as a systemd service:

```bash
# Copy the service file to the systemd directory
sudo cp scripts/twinshare-rest-api.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable twinshare-rest-api

# Start the service
sudo systemctl start twinshare-rest-api

# Check the service status
sudo systemctl status twinshare-rest-api
```

## Authentication

Currently, the API does not implement authentication. It is recommended to run the API server on a secure network or behind a reverse proxy that handles authentication.

Future versions will include authentication mechanisms such as:
- API key authentication
- OAuth 2.0
- JWT tokens

## API Endpoints

All endpoints return JSON responses. Successful responses have a status code of 200 and include relevant data. Error responses include an `error` field with a description of the error.

### Root Endpoint

```
GET /
```

Returns basic information about the API.

**Response:**

```json
{
  "name": "AI Environment Manager API",
  "version": "0.1.0",
  "endpoints": [
    "/api/vm",
    "/api/p2p",
    "/api/remote"
  ]
}
```

### VM Management

#### List VMs

```
GET /api/vm
```

Returns a list of all virtual machines.

**Response:**

```json
{
  "vms": [
    {
      "id": "vm-123",
      "name": "example-vm",
      "status": "running",
      "cpu_cores": 2,
      "memory": 2048,
      "disk_size": 20,
      "hypervisor": "kvm",
      "network": "default",
      "vnc_port": 5900,
      "created_at": "2025-05-10T10:30:00Z"
    },
    ...
  ]
}
```

#### Create VM

```
POST /api/vm
```

Creates a new virtual machine.

**Request Body:**

```json
{
  "name": "new-vm",
  "image": "ubuntu-20.04",
  "cpu_cores": 2,
  "memory": 2048,
  "disk_size": 20,
  "network": "default",
  "hypervisor": "kvm"
}
```

**Required Fields:**
- `name`: Name of the virtual machine
- `image`: Base image to use

**Optional Fields:**
- `cpu_cores`: Number of CPU cores (default: 2)
- `memory`: Amount of RAM in MB (default: 2048)
- `disk_size`: Disk size in GB (default: 20)
- `network`: Network name (default: "default")
- `hypervisor`: Hypervisor type (default: "kvm")

**Response:**

```json
{
  "id": "vm-456",
  "name": "new-vm",
  "status": "stopped",
  "cpu_cores": 2,
  "memory": 2048,
  "disk_size": 20,
  "hypervisor": "kvm",
  "network": "default",
  "vnc_port": null,
  "created_at": "2025-05-11T14:20:00Z"
}
```

#### Get VM Status

```
GET /api/vm/{name}
```

Returns the status of a specific virtual machine.

**Path Parameters:**
- `name`: Name of the virtual machine

**Response:**

```json
{
  "id": "vm-123",
  "name": "example-vm",
  "status": "running",
  "cpu_cores": 2,
  "memory": 2048,
  "disk_size": 20,
  "hypervisor": "kvm",
  "network": "default",
  "vnc_port": 5900,
  "created_at": "2025-05-10T10:30:00Z",
  "uptime": 3600
}
```

#### Start VM

```
POST /api/vm/{name}/start
```

Starts a virtual machine.

**Path Parameters:**
- `name`: Name of the virtual machine

**Response:**

```json
{
  "success": true,
  "name": "example-vm",
  "status": "running",
  "vnc_port": 5900
}
```

#### Stop VM

```
POST /api/vm/{name}/stop
```

Stops a virtual machine.

**Path Parameters:**
- `name`: Name of the virtual machine

**Request Body (optional):**

```json
{
  "force": false
}
```

**Optional Fields:**
- `force`: Whether to force stop the VM (default: false)

**Response:**

```json
{
  "success": true,
  "name": "example-vm",
  "status": "stopped"
}
```

#### Delete VM

```
DELETE /api/vm/{name}
```

Deletes a virtual machine.

**Path Parameters:**
- `name`: Name of the virtual machine

**Request Body (optional):**

```json
{
  "delete_disk": true
}
```

**Optional Fields:**
- `delete_disk`: Whether to delete the VM's disk (default: true)

**Response:**

```json
{
  "success": true,
  "name": "example-vm"
}
```

### P2P Networking

#### Get Local Peer Info

```
GET /api/p2p/info
```

Returns information about the local P2P node.

**Response:**

```json
{
  "id": "peer-123",
  "name": "local-node",
  "address": "192.168.1.100",
  "port": 8000,
  "status": "online",
  "services": ["vm", "discovery"],
  "uptime": 3600
}
```

#### List Peers

```
GET /api/p2p/peers
```

Returns a list of all peers in the P2P network.

**Response:**

```json
{
  "peers": [
    {
      "id": "peer-456",
      "name": "remote-node-1",
      "address": "192.168.1.101",
      "port": 8000,
      "status": "online",
      "services": ["vm", "discovery"],
      "last_seen": "2025-05-11T14:20:00Z"
    },
    ...
  ]
}
```

#### Start P2P Services

```
POST /api/p2p/start
```

Starts the P2P services.

**Response:**

```json
{
  "success": true,
  "status": "started",
  "id": "peer-123",
  "address": "192.168.1.100",
  "port": 8000
}
```

#### Stop P2P Services

```
POST /api/p2p/stop
```

Stops the P2P services.

**Response:**

```json
{
  "success": true,
  "status": "stopped"
}
```

#### Send Message

```
POST /api/p2p/message
```

Sends a message to a peer.

**Request Body:**

```json
{
  "peer_id": "peer-456",
  "message_type": "HELLO",
  "data": {
    "message": "Hello from REST API!"
  }
}
```

**Required Fields:**
- `peer_id`: ID of the target peer
- `message_type`: Type of message to send
- `data`: Message data (can be any JSON object)

**Response:**

```json
{
  "response": {
    "status": "ok",
    "message": "Hello received"
  }
}
```

### Remote VM Management

#### List Remote VMs

```
GET /api/remote/{peer_id}/vm
```

Returns a list of virtual machines on a remote peer.

**Path Parameters:**
- `peer_id`: ID of the remote peer

**Response:**

```json
{
  "vms": [
    {
      "id": "vm-789",
      "name": "remote-vm",
      "status": "running",
      "cpu_cores": 2,
      "memory": 2048,
      "disk_size": 20,
      "hypervisor": "kvm",
      "network": "default",
      "vnc_port": 5900,
      "created_at": "2025-05-10T10:30:00Z"
    },
    ...
  ]
}
```

#### Create Remote VM

```
POST /api/remote/{peer_id}/vm
```

Creates a new virtual machine on a remote peer.

**Path Parameters:**
- `peer_id`: ID of the remote peer

**Request Body:**

```json
{
  "name": "new-remote-vm",
  "image": "ubuntu-20.04",
  "cpu_cores": 2,
  "memory": 2048,
  "disk_size": 20,
  "network": "default",
  "hypervisor": "kvm"
}
```

**Required Fields:**
- `name`: Name of the virtual machine
- `image`: Base image to use

**Optional Fields:**
- `cpu_cores`: Number of CPU cores (default: 2)
- `memory`: Amount of RAM in MB (default: 2048)
- `disk_size`: Disk size in GB (default: 20)
- `network`: Network name (default: "default")
- `hypervisor`: Hypervisor type (default: "kvm")

**Response:**

```json
{
  "success": true,
  "peer_id": "peer-456",
  "vm_id": "vm-789",
  "name": "new-remote-vm",
  "status": "stopped"
}
```

#### Start Remote VM

```
POST /api/remote/{peer_id}/vm/{vm_id}/start
```

Starts a virtual machine on a remote peer.

**Path Parameters:**
- `peer_id`: ID of the remote peer
- `vm_id`: ID of the virtual machine

**Response:**

```json
{
  "success": true,
  "peer_id": "peer-456",
  "vm_id": "vm-789",
  "name": "remote-vm",
  "status": "running"
}
```

#### Stop Remote VM

```
POST /api/remote/{peer_id}/vm/{vm_id}/stop
```

Stops a virtual machine on a remote peer.

**Path Parameters:**
- `peer_id`: ID of the remote peer
- `vm_id`: ID of the virtual machine

**Request Body (optional):**

```json
{
  "force": false
}
```

**Optional Fields:**
- `force`: Whether to force stop the VM (default: false)

**Response:**

```json
{
  "success": true,
  "peer_id": "peer-456",
  "vm_id": "vm-789",
  "name": "remote-vm",
  "status": "stopped"
}
```

#### Delete Remote VM

```
DELETE /api/remote/{peer_id}/vm/{vm_id}
```

Deletes a virtual machine on a remote peer.

**Path Parameters:**
- `peer_id`: ID of the remote peer
- `vm_id`: ID of the virtual machine

**Request Body (optional):**

```json
{
  "delete_disk": true
}
```

**Optional Fields:**
- `delete_disk`: Whether to delete the VM's disk (default: true)

**Response:**

```json
{
  "success": true,
  "peer_id": "peer-456",
  "vm_id": "vm-789",
  "name": "remote-vm"
}
```

## Error Handling

The API returns appropriate HTTP status codes for errors:

- `400 Bad Request`: Invalid request parameters or JSON
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include an `error` field with a description of the error:

```json
{
  "error": "Virtual machine 'non-existent-vm' not found"
}
```

Common error scenarios:
- Missing required fields in request body
- Invalid JSON format
- VM not found
- P2P services not running
- Remote peer not available

## Examples

### Using cURL

#### List VMs

```bash
curl -X GET http://localhost:8080/api/vm
```

#### Create VM

```bash
curl -X POST http://localhost:8080/api/vm \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-vm",
    "image": "ubuntu-20.04",
    "cpu_cores": 2,
    "memory": 2048,
    "disk_size": 20
  }'
```

#### Start VM

```bash
curl -X POST http://localhost:8080/api/vm/new-vm/start
```

#### Stop VM with Force Option

```bash
curl -X POST http://localhost:8080/api/vm/new-vm/stop \
  -H "Content-Type: application/json" \
  -d '{
    "force": true
  }'
```

#### Delete VM

```bash
curl -X DELETE http://localhost:8080/api/vm/new-vm
```

#### Start P2P Services

```bash
curl -X POST http://localhost:8080/api/p2p/start
```

### Using Python

See the `examples/rest_api_usage.py` file for a complete example of using the REST API with Python.

Basic usage:

```python
import asyncio
from src.api.rest_client import RESTClient

async def main():
    async with RESTClient("http://localhost:8080") as client:
        # List VMs
        vms = await client.list_vms()
        print(vms)
        
        # Create VM
        vm = await client.create_vm(
            name="example-vm",
            image="ubuntu-20.04",
            cpu_cores=2,
            memory=2048,
            disk_size=20
        )
        print(vm)
        
        # Start VM
        result = await client.start_vm("example-vm")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Client Libraries

twinshare provides a Python client library for the REST API:

```python
from src.api.rest_client import RESTClient

async with RESTClient("http://localhost:8080") as client:
    # List VMs
    vms = await client.list_vms()
    print(vms)
    
    # Create VM
    vm = await client.create_vm(
        name="example-vm",
        image="ubuntu-20.04",
        cpu_cores=2,
        memory=2048,
        disk_size=20
    )
    print(vm)
```

The client library provides methods for all API endpoints and handles error handling, session management, and JSON parsing.

For more examples, see the `examples/rest_api_usage.py` file.

## Rate Limiting

Currently, the API does not implement rate limiting. Future versions may include rate limiting to prevent abuse.

## Versioning

The current API version is v1, which is implicitly used in all endpoints. Future versions may include explicit versioning in the URL path (e.g., `/api/v2/vm`).

API changes will be documented in the changelog and will follow semantic versioning principles.
