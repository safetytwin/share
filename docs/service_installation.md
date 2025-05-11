# twinshare REST API Service Installation Guide

This guide provides step-by-step instructions for installing and configuring the twinshare REST API as a system service.

## Prerequisites

- Linux system with systemd (Ubuntu, Fedora, CentOS, etc.)
- Python 3.6 or higher
- sudo privileges

## Quick Installation

For a quick installation, use the provided script:

```bash
# Navigate to the project directory
cd /path/to/twinshare/share

# Make the script executable if needed
chmod +x start_service.sh

# Run the service installation script
sudo ./start_service.sh
```

## Manual Installation Steps

If you prefer to install the service manually or if the script doesn't work, follow these steps:

### 1. Create Required Directories

First, create the directories for logs and PID files:

```bash
sudo mkdir -p /var/log/twinshare /var/run/twinshare
sudo chown $USER:$USER /var/log/twinshare /var/run/twinshare
```

### 2. Install the Service File

Create a systemd service file for the REST API:

```bash
# Navigate to the project directory
cd /path/to/twinshare/share

# Get the absolute path to the project directory
PROJECT_DIR=$(pwd)

# Create a temporary service file with your username and the correct path
cat scripts/twinshare-rest-api.service | \
    sed "s/\$USER/$USER/g" | \
    sed "s|/home/tom/github/twinshare/share|$PROJECT_DIR|g" > /tmp/twinshare-rest-api.service

# Copy the service file to the systemd directory
sudo cp /tmp/twinshare-rest-api.service /etc/systemd/system/twinshare-rest-api.service

# Clean up
rm /tmp/twinshare-rest-api.service
```

### 3. Reload Systemd Configuration

```bash
sudo systemctl daemon-reload
```

### 4. Enable and Start the Service

```bash
# Enable the service to start on boot
sudo systemctl enable twinshare-rest-api

# Start the service
sudo systemctl start twinshare-rest-api
```

### 5. Verify the Service Status

```bash
sudo systemctl status twinshare-rest-api
```

You should see output indicating that the service is active (running).

## Managing the Service

### Checking Status

```bash
sudo systemctl status twinshare-rest-api
```

### Stopping the Service

```bash
sudo systemctl stop twinshare-rest-api
```

### Restarting the Service

```bash
sudo systemctl restart twinshare-rest-api
```

### Viewing Logs

```bash
# View all logs
sudo journalctl -u twinshare-rest-api

# View recent logs and follow new entries
sudo journalctl -u twinshare-rest-api -f

# View logs since a specific time
sudo journalctl -u twinshare-rest-api --since "2025-05-11 18:00:00"
```

## Troubleshooting

### Service Fails to Start

If the service fails to start, check the logs for errors:

```bash
sudo journalctl -u twinshare-rest-api -n 50
```

Common issues include:

1. **Path problems**: The service file might contain incorrect paths. Make sure to replace `/home/tom/github/twinshare/share` with your actual project path.

2. **Missing directories**: Ensure `/var/log/twinshare` and `/var/run/twinshare` exist and have the correct permissions.

3. **Python environment issues**: The service might not have access to the required Python packages. Make sure the service file is using the Python from the virtual environment:

   ```
   ExecStart=/path/to/safetytwin/share/venv/bin/python3 /path/to/safetytwin/share/scripts/start_rest_api.py start --log-file /var/log/safetytwin/rest_api.log --pid-file /var/run/safetytwin/rest_api.pid
   ```

4. **Module import errors**: 

   a. **Missing python-daemon**: If you see "ModuleNotFoundError: No module named 'daemon'" in the logs, it means the `python-daemon` package is not installed. Install it with:

   ```bash
   # Activate the virtual environment
   source /path/to/safetytwin/share/venv/bin/activate
   
   # Install the python-daemon package
   pip install python-daemon
   
   # Deactivate the virtual environment
   deactivate
   ```

   b. **aiohttp.web import error**: If you see "AttributeError: module aiohttp has no attribute web" in the logs, it means there's an import issue with the aiohttp package. This can be fixed by:

   1. Making sure you have the correct version of aiohttp installed:
   
   ```bash
   source /path/to/safetytwin/share/venv/bin/activate
   pip install "aiohttp[speedups]<4.0.0,>=3.8.0" aiohttp-cors>=0.7.0
   deactivate
   ```
   
   2. Updating the import statement in the network.py file:
   
   ```python
   # Change this:
   import aiohttp
   # ...and later using aiohttp.web
   
   # To this:
   import aiohttp
   from aiohttp import web
   # ...and later using just web
   ```

5. **Permission problems**: Ensure the user specified in the service file has the necessary permissions to run the REST API.

### Modifying the Service Configuration

If you need to modify the service configuration:

1. Edit the service file:

   ```bash
   sudo nano /etc/systemd/system/safetytwin-rest-api.service
   ```

2. Reload the systemd configuration:

   ```bash
   sudo systemctl daemon-reload
   ```

3. Restart the service:

   ```bash
   sudo systemctl restart safetytwin-rest-api
   ```

## Manual Operation (Without Systemd)

If you prefer to run the REST API without using systemd, you can use the following commands:

```bash
# Start in foreground mode
python3 scripts/start_rest_api.py start --foreground

# Start as a daemon
python3 scripts/start_rest_api.py start

# Check status
python3 scripts/start_rest_api.py status

# Stop the daemon
python3 scripts/start_rest_api.py stop
```

## Next Steps

After successfully installing the REST API service, you can:

1. Test the API using the examples in `examples/rest_api_usage.py`
2. Refer to the [REST API Guide](rest_api_guide.md) for detailed API documentation
3. Integrate the API with your applications using the provided client library
