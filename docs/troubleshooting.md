# twinshare Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using the twinshare application.

## Table of Contents
- [Service Issues](#service-issues)
- [VM Management Issues](#vm-management-issues)
- [P2P Network Issues](#p2p-network-issues)
- [SSL Configuration Issues](#ssl-configuration-issues)
- [Permission Problems](#permission-problems)
- [Common Error Messages](#common-error-messages)
- [CLI Command Issues](#cli-command-issues)

## Service Issues

### Service Fails to Start

**Symptoms:**
- `systemctl status twinshare-rest-api` shows "failed" status
- Service repeatedly restarts and fails

**Solutions:**

1. **Check for missing directories:**
   ```bash
   sudo mkdir -p /var/log/twinshare /var/run/twinshare
   sudo chown $USER:$USER /var/log/twinshare /var/run/twinshare
   ```

2. **Check service logs:**
   ```bash
   sudo journalctl -u twinshare-rest-api -n 50
   ```

3. **Unmask the service if it's masked:**
   ```bash
   sudo systemctl unmask twinshare-rest-api.service
   sudo systemctl daemon-reload
   ```

4. **Verify service file exists and has correct paths:**
   ```bash
   sudo cat /etc/systemd/system/twinshare-rest-api.service
   ```
   
   Make sure paths match your actual installation directory.

5. **Fix PID file issues:**
   If you see errors about PID files, ensure the directory exists and has proper permissions:
   ```bash
   sudo mkdir -p /run/twinshare
   sudo chmod 755 /run/twinshare
   sudo chown $USER:$USER /run/twinshare
   ```

### Service Starts But API is Unreachable

**Symptoms:**
- Service appears to be running but API calls fail
- Connection refused errors

**Solutions:**

1. **Check if the API is listening on the correct interface:**
   ```bash
   netstat -tuln | grep 37780
   ```
   
   If it's only listening on 127.0.0.1, modify the configuration to listen on all interfaces:
   ```bash
   twinshare config set api.host 0.0.0.0
   ```

2. **Check firewall settings:**
   ```bash
   sudo ufw status
   ```
   
   If needed, allow the API port:
   ```bash
   sudo ufw allow 37780/tcp
   ```

## VM Management Issues

### Cannot Create VMs

**Symptoms:**
- VM creation fails with error messages
- Insufficient resources errors

**Solutions:**

1. **Check available disk space:**
   ```bash
   df -h
   ```

2. **Check memory and CPU resources:**
   ```bash
   free -h
   nproc
   ```

3. **Verify libvirt is running:**
   ```bash
   systemctl status libvirtd
   ```
   
   If not running:
   ```bash
   sudo systemctl start libvirtd
   ```

4. **Check user permissions for libvirt:**
   ```bash
   groups
   ```
   
   Ensure your user is in the libvirt group:
   ```bash
   sudo usermod -aG libvirt $USER
   ```
   (Log out and back in for changes to take effect)

### VMs Start But Are Not Accessible

**Symptoms:**
- VM appears to be running but cannot be accessed via network
- Console access works but network doesn't

**Solutions:**

1. **Check VM network configuration:**
   ```bash
   twinshare vm network-info <vm-name>
   ```

2. **Verify bridge network is properly configured:**
   ```bash
   ip a
   ```

3. **Check if VM has an IP address:**
   ```bash
   twinshare vm ip <vm-name>
   ```

## P2P Network Issues

### Peers Cannot Discover Each Other

**Symptoms:**
- `twinshare p2p list` shows no peers
- Cannot connect to remote peers

**Solutions:**

1. **Check if P2P discovery is enabled:**
   ```bash
   twinshare config get p2p.discovery.enable
   ```
   
   If disabled, enable it:
   ```bash
   twinshare config set p2p.discovery.enable true
   ```

2. **Check network configuration:**
   ```bash
   twinshare config get p2p.discovery.networks
   ```
   
   Add your network if needed:
   ```bash
   twinshare config set p2p.discovery.networks '["192.168.1.0/24"]'
   ```

3. **Check firewall settings:**
   ```bash
   sudo ufw status
   ```
   
   Allow P2P discovery port:
   ```bash
   sudo ufw allow 37777/udp
   ```

### Cannot Access Remote VMs

**Symptoms:**
- Remote VMs are visible but operations fail
- Authentication errors when accessing remote VMs

**Solutions:**

1. **Check if the workspace is shared:**
   ```bash
   curl -X GET http://localhost:37780/shared
   ```

2. **Enable workspace sharing if needed:**
   ```bash
   curl -X POST http://localhost:37780/shared/<workspace_name> -H "Content-Type: application/json" -d '{"enable": true}'
   ```

3. **Check authentication settings:**
   ```bash
   twinshare config get api.use_auth
   twinshare config get api.key
   ```

## SSL Configuration Issues

### SSL Certificate Errors

**Symptoms:**
- Service fails to start with SSL-related errors
- "Config object has no attribute" errors related to SSL

**Solutions:**

1. **Check SSL configuration:**
   ```bash
   twinshare config get p2p.network.ssl
   ```
   
   If missing, add it:
   ```bash
   twinshare config set p2p.network.ssl false
   ```

2. **Generate new SSL certificates:**
   ```bash
   # First, stop the service
   sudo systemctl stop twinshare-rest-api
   
   # Remove existing certificates
   rm -f ~/.ai-environment/certificates/server.crt ~/.ai-environment/certificates/server.key
   
   # Start the service (it will generate new certificates)
   sudo systemctl start twinshare-rest-api
   ```

## Permission Problems

### File Permission Errors

**Symptoms:**
- "Permission denied" errors in logs
- Cannot write to log or PID files

**Solutions:**

1. **Check and fix directory permissions:**
   ```bash
   sudo mkdir -p /var/log/twinshare /var/run/twinshare
   sudo chown $USER:$USER /var/log/twinshare /var/run/twinshare
   sudo chmod 755 /var/log/twinshare /var/run/twinshare
   ```

2. **Check configuration directory permissions:**
   ```bash
   ls -la ~/.ai-environment
   ```
   
   Fix if needed:
   ```bash
   chmod 700 ~/.ai-environment
   ```

### Libvirt Permission Issues

**Symptoms:**
- "Permission denied" when accessing libvirt
- Cannot create or manage VMs

**Solutions:**

1. **Add user to libvirt group:**
   ```bash
   sudo usermod -aG libvirt $USER
   sudo usermod -aG kvm $USER
   ```
   (Log out and back in for changes to take effect)

2. **Check libvirt socket permissions:**
   ```bash
   ls -la /var/run/libvirt/libvirt-sock
   ```

## Common Error Messages

### "Config object has no attribute..."

This usually indicates a missing configuration key.

**Solution:**
Add the missing configuration key:
```bash
twinshare config set <missing.key> <appropriate_value>
```

For example:
```bash
twinshare config set p2p.network.ssl false
```

### "Unit twinshare-rest-api.service is masked"

The service has been explicitly disabled at the system level.

**Solution:**
```bash
sudo systemctl unmask twinshare-rest-api.service
sudo systemctl daemon-reload
sudo systemctl start twinshare-rest-api.service
```

### "Can't open PID file '/run/twinshare/rest_api.pid' (yet?) after start"

The PID directory doesn't exist or has incorrect permissions.

**Solution:**
```bash
sudo mkdir -p /run/twinshare
sudo chmod 755 /run/twinshare
sudo chown $USER:$USER /run/twinshare
sudo systemctl restart twinshare-rest-api
```

### "Connection refused" when accessing API

The API service isn't running or is only listening on localhost.

**Solution:**
```bash
# Check if service is running
systemctl status twinshare-rest-api

# Configure API to listen on all interfaces
twinshare config set api.host 0.0.0.0
twinshare config set api.allow_remote true

# Restart the service
sudo systemctl restart twinshare-rest-api
```

## CLI Command Issues

### "Command not found: twinshare"

**Symptoms:**
- After installation, the `twinshare` command is not found
- You get a "command not found" error when trying to run twinshare commands

**Solutions:**

1. **Make sure your virtual environment is activated:**
   ```bash
   source venv/bin/activate
   ```

2. **If the command is still not found, create a wrapper script:**
   ```bash
   # Run the fix script
   ./fix_twinshare_cli.sh
   
   # This creates a twinshare command in the current directory
   # You can then use it with:
   ./twinshare <command>
   ```

3. **Ensure ~/.local/bin is in your PATH if you want to use the command globally:**
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### "Invalid choice: 'api' (choose from 'vm', 'p2p', 'remote')"

**Symptoms:**
- When trying to run `twinshare api start`, you get an error about 'api' being an invalid choice

**Solutions:**

1. **The twinshare CLI doesn't have an "api" command. Instead, use the provided script to manage the API service:**
   ```bash
   # Start the API service
   ./start_api.sh start
   
   # Check the status
   ./start_api.sh status
   
   # Stop the API service
   ./start_api.sh stop
   ```

2. **Alternatively, you can directly use the REST API script:**
   ```bash
   python3 scripts/start_rest_api.py start --host 0.0.0.0 --port 37780
   ```

3. **For a system-wide installation, use the systemd service:**
   ```bash
   sudo systemctl start twinshare-rest-api
   ```

## Getting Help

If you continue to experience issues after trying these troubleshooting steps, please:

1. Gather relevant logs:
   ```bash
   sudo journalctl -u twinshare-rest-api -n 100 > twinshare-service.log
   cat ~/.ai-environment/logs/api.log > twinshare-api.log
   ```

2. Create a detailed description of the issue, including:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Error messages
   - System information (OS, version, etc.)

3. Submit an issue with this information to the project repository or contact support.
