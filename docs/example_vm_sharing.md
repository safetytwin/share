# twinshare VM Creation and Sharing Example

This guide provides a complete walkthrough for creating a virtual machine and sharing it with other users on your network using twinshare.

## Prerequisites

Before starting, ensure that:
- twinshare is properly installed
- The REST API service is running
- You have sufficient resources (CPU, RAM, disk space) for VM creation
- You have the necessary permissions to create and manage VMs

## Step 1: Start the twinshare Services

First, ensure that the twinshare REST API service is running:

```bash
# Check service status
systemctl status twinshare-rest-api

# If not running, start it
sudo systemctl start twinshare-rest-api
```

## Step 2: Create a Workspace

Workspaces organize your VMs and make sharing easier. Let's create a workspace called "demo-workspace":

```bash
# Create a new workspace
twinshare workspace create demo-workspace

# Verify the workspace was created
twinshare workspace list
```

Expected output:
```
Available workspaces:
- demo-workspace (0 VMs)
```

## Step 3: Create a Virtual Machine

Now, let's create a Ubuntu 22.04 VM in our workspace:

```bash
# Create a VM with 2 CPUs, 2GB RAM, and 20GB disk
twinshare vm create --workspace demo-workspace --name ubuntu-demo \
  --image ubuntu-22.04 --cpu 2 --memory 2048 --disk 20
```

This command will:
1. Download the Ubuntu 22.04 image (if not already available)
2. Create a new VM with the specified resources
3. Add it to the demo-workspace

Expected output:
```
Creating VM 'ubuntu-demo' in workspace 'demo-workspace'...
Downloading image 'ubuntu-22.04'... Done
Allocating resources... Done
VM 'ubuntu-demo' created successfully.
```

## Step 4: Start the VM

Let's start the VM we just created:

```bash
# Start the VM
twinshare vm start --workspace demo-workspace ubuntu-demo
```

Expected output:
```
Starting VM 'ubuntu-demo'...
VM started successfully.
```

## Step 5: Check VM Status

Verify that the VM is running:

```bash
# Check VM status
twinshare vm status --workspace demo-workspace ubuntu-demo
```

Expected output:
```
VM: ubuntu-demo
Status: running
IP Address: 192.168.122.xxx
CPU: 2 vCPUs
Memory: 2048 MB
Disk: 20 GB
```

## Step 6: Share the Workspace

Now that we have a running VM, let's share the workspace so others can access it:

```bash
# Share the workspace using the REST API
curl -X POST http://localhost:37780/shared/demo-workspace \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'
```

Expected output:
```json
{
  "status": "success",
  "message": "Workspace 'demo-workspace' is now shared"
}
```

Alternatively, you can use the CLI if available:

```bash
# Using the CLI to share a workspace
twinshare workspace share --name demo-workspace
```

## Step 7: Verify Sharing Status

Check that the workspace is properly shared:

```bash
# List shared workspaces
curl -X GET http://localhost:37780/shared
```

Expected output:
```json
{
  "shared_workspaces": [
    {
      "name": "demo-workspace",
      "vm_count": 1
    }
  ]
}
```

## Step 8: Access the VM from Another Machine

On another machine in the same network, users can now access your shared VM:

```bash
# List available peers (run on the other machine)
twinshare p2p list
```

Expected output:
```
Available peers:
- Node: user-desktop (192.168.1.100)
  ID: a1b2c3d4-e5f6-7890-abcd-1234567890ab
  Shared workspaces: 1
```

```bash
# List VMs shared by the peer (run on the other machine)
twinshare remote vm-list --peer 192.168.1.100
```

Expected output:
```
Remote VMs from peer 192.168.1.100:
Workspace: demo-workspace
- ubuntu-demo (running)
  CPU: 2 vCPUs
  Memory: 2048 MB
  Disk: 20 GB
```

## Step 9: Start the Remote VM (if needed)

If the VM is not already running, the remote user can start it:

```bash
# Start the remote VM (run on the other machine)
twinshare remote vm-start --peer 192.168.1.100 --name ubuntu-demo
```

Expected output:
```
Starting remote VM 'ubuntu-demo' on peer 192.168.1.100...
VM started successfully.
```

## Step 10: Connect to the VM

The remote user can now connect to the VM using SSH, VNC, or other remote access tools:

```bash
# Get the VM's IP address (run on the other machine)
twinshare remote vm-info --peer 192.168.1.100 --name ubuntu-demo
```

Expected output:
```
VM: ubuntu-demo
Status: running
IP Address: 192.168.122.xxx
CPU: 2 vCPUs
Memory: 2048 MB
Disk: 20 GB
```

```bash
# Connect via SSH (if SSH is configured on the VM)
ssh ubuntu@192.168.122.xxx
```

## Step 11: Stop Sharing When Done

When you no longer want to share the VM, disable sharing for the workspace:

```bash
# Disable sharing for the workspace
curl -X POST http://localhost:37780/shared/demo-workspace \
  -H "Content-Type: application/json" \
  -d '{"enable": false}'
```

Or using the CLI:

```bash
# Using the CLI to unshare a workspace
twinshare workspace unshare --name demo-workspace
```

## Step 12: Clean Up (Optional)

If you want to remove the VM and workspace:

```bash
# Stop the VM first
twinshare vm stop --workspace demo-workspace ubuntu-demo

# Delete the VM
twinshare vm delete --workspace demo-workspace ubuntu-demo

# Delete the workspace
twinshare workspace delete demo-workspace
```

## Troubleshooting

If you encounter issues during this process, refer to the [Troubleshooting Guide](troubleshooting.md) for solutions to common problems.

### Common Issues:

1. **VM creation fails**: Check available resources and libvirt permissions.
2. **Sharing doesn't work**: Ensure the API service is running and accessible.
3. **Remote peer can't see shared VMs**: Check network configuration and firewall settings.
4. **Cannot connect to VM**: Verify the VM has a valid IP address and network connectivity.

## Advanced Configuration

For more control over VM sharing, you can configure:

- **Authentication**: Enable API authentication for secure sharing
  ```bash
  twinshare config set api.use_auth true
  twinshare config set api.key "your-secure-api-key"
  ```

- **Network Restrictions**: Limit which networks can discover your shared VMs
  ```bash
  twinshare config set p2p.discovery.networks '["192.168.1.0/24"]'
  ```

- **Resource Limits**: Set limits on how much resources remote users can use
  ```bash
  twinshare config set resources.remote.max_cpu 4
  twinshare config set resources.remote.max_memory 4096
  ```

## Next Steps

After mastering basic VM sharing, explore these advanced features:

- Creating VM templates for quick deployment
- Setting up automated backups for shared VMs
- Configuring VM resource limits and quotas
- Implementing custom authentication for secure sharing
