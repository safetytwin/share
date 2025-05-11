# twinshare VM Sharing Guide

This guide explains how to use the twinshare solution to share and manage virtual machines across a network.

## Installation

### Installing on a New System

To install twinshare on a new system, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/safetytwin/share.git
   cd share
   ```

2. Run the installation script:
   ```bash
   ./install_package.sh
   ```
   
   This script will:
   - Check for required dependencies
   - Install the package either in a virtual environment or system-wide
   - Create the necessary symlinks for the CLI command
   - Test the installation

3. Verify the installation:
   ```bash
   twinshare --help
   ```

### Troubleshooting Installation Issues

If the `twinshare` command is not available after installation:

1. Make sure the installation script completed successfully
2. Check if the symlink was created:
   ```bash
   which twinshare
   ```
3. If using a virtual environment, ensure it's activated:
   ```bash
   source venv/bin/activate
   ```
4. Try running the CLI directly:
   ```bash
   python3 -m src.cli.main --help
   ```

## Prerequisites

Before using the VM sharing functionality, ensure that:

1. The twinshare REST API service is running
2. Your network allows connections to the API port (default: 37780)
3. You have the twinshare CLI installed and configured

## Starting the API Server

If the API server is not running as a system service, start it manually:

```bash
twinshare api start
```

To check if the service is running:

```bash
systemctl status twinshare-rest-api
```

## Sharing Workspaces

A workspace is a collection of VMs and resources. You need to share a workspace before its VMs can be accessed remotely.

### Using the REST API

#### Enable Sharing for a Workspace

```bash
curl -X POST http://localhost:37780/shared/my_workspace -H "Content-Type: application/json" -d '{"enable": true}'
```

#### Disable Sharing for a Workspace

```bash
curl -X POST http://localhost:37780/shared/my_workspace -H "Content-Type: application/json" -d '{"enable": false}'
```

Or use the DELETE method:

```bash
curl -X DELETE http://localhost:37780/shared/my_workspace
```

### Using the CLI (if available)

```bash
# Share a workspace
twinshare workspace share --name my_workspace
twinshare workspace share --name test-vm

# Unshare a workspace
twinshare workspace unshare --name my_workspace
```

## Managing Remote VMs

Once a workspace is shared, you can manage its VMs from other machines using the twinshare CLI.

### List Available Remote VMs

```bash
twinshare remote vm-list --peer <peer_address>
```

Example:
```bash
twinshare remote vm-list --peer 192.168.1.100
```

### Create a VM on a Remote Peer

```bash
twinshare remote vm-create --peer <peer_address> --name <vm_name> --image <image_name> --memory <memory_size> --vcpus <num_cpus>
```

Example:
```bash
twinshare remote vm-create --peer 192.168.1.100 --name test-vm --image ubuntu-20.04 --memory 2048 --vcpus 2
```

### Start a Remote VM

```bash
twinshare remote vm-start --peer <peer_address> --name <vm_name>
```

Example:
```bash
twinshare remote vm-start --peer 192.168.1.100 --name test-vm
```

### Stop a Remote VM

```bash
twinshare remote vm-stop --peer <peer_address> --name <vm_name> [--force]
```

Example:
```bash
twinshare remote vm-stop --peer 192.168.1.100 --name test-vm
```

Use the `--force` flag to force stop a VM that is not responding:
```bash
twinshare remote vm-stop --peer 192.168.1.100 --name test-vm --force
```

### Delete a Remote VM

```bash
twinshare remote vm-delete --peer <peer_address> --name <vm_name> [--force]
```

Example:
```bash
twinshare remote vm-delete --peer 192.168.1.100 --name test-vm
```

## Authentication

If authentication is enabled, you need to include an API key in your requests.

### REST API with Authentication

```bash
curl -X POST http://localhost:37780/shared/my_workspace \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"enable": true}'
```

### CLI with Authentication

Set the API key in your configuration or use the `--api-key` flag:

```bash
twinshare remote vm-list --peer 192.168.1.100 --api-key YOUR_API_KEY
```

## Troubleshooting

### Service Not Starting

If the twinshare REST API service fails to start, check the logs:

```bash
journalctl -u twinshare-rest-api -n 50
```

Common issues include:
- Permission problems with PID file or log directories
- SSL configuration errors
- Port conflicts

### Connection Issues

If you cannot connect to a remote peer:
1. Ensure the peer's API service is running
2. Check that the peer's firewall allows connections to port 37780
3. Verify that the workspace is properly shared
4. Check network connectivity between the machines

### Authentication Errors

If you receive "Unauthorized" errors:
1. Verify that your API key is correct
2. Check that the API key is properly configured on the server
3. Ensure you're using the correct format for the Authorization header

## Configuration

You can customize the twinshare VM sharing behavior by editing the configuration:

```bash
# View current configuration
twinshare config show

# Set configuration values
twinshare config set api.port 37781
twinshare config set api.use_auth true
twinshare config set api.key "your-secure-api-key"
```

## Security Recommendations

1. Enable authentication for production environments
2. Use a strong, unique API key
3. Limit access to the API port using firewall rules
4. Consider using SSL for the API server in production
5. Regularly review which workspaces are being shared
