#!/bin/bash
# Installation script for twinshare package
# This script ensures the package is properly installed with the CLI command available

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${GREEN}[twinshare]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. It's recommended to install as a regular user with sudo privileges."
    read -p "Continue as root? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_message "Exiting."
        exit 1
    fi
fi

# Get the project directory
PROJECT_DIR=$(pwd)
print_message "Project directory: $PROJECT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 is not installed. Attempting to install..."
    if [ "$EUID" -eq 0 ]; then
        apt-get update && apt-get install -y python3-pip
    else
        sudo apt-get update && sudo apt-get install -y python3-pip
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_error "Failed to install pip3. Please install it manually and try again."
        exit 1
    fi
fi

# Check if virtual environment is needed
read -p "Install in a virtual environment? (recommended) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if virtualenv is installed
    if ! command -v virtualenv &> /dev/null; then
        print_warning "virtualenv is not installed. Attempting to install..."
        pip3 install virtualenv
        
        if ! command -v virtualenv &> /dev/null; then
            print_error "Failed to install virtualenv. Please install it manually and try again."
            exit 1
        fi
    fi
    
    # Create virtual environment
    print_message "Creating virtual environment..."
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Using existing environment."
    else
        virtualenv venv
    fi
    
    # Activate virtual environment
    print_message "Activating virtual environment..."
    source venv/bin/activate
    
    # Install package in development mode
    print_message "Installing package in development mode..."
    pip install -e .
    
    # Explicitly install all required dependencies
    print_message "Installing required dependencies..."
    pip install pyyaml aiohttp asyncio tabulate cryptography python-daemon netifaces
    
    # Create symlink to the CLI script
    print_message "Creating symlink to the CLI script..."
    if [ -f "venv/bin/twinshare" ]; then
        print_warning "Symlink already exists."
    else
        ln -s "$PROJECT_DIR/bin/twinshare" "venv/bin/twinshare"
        chmod +x "venv/bin/twinshare"
    fi
    
    print_message "Installation complete!"
    print_message "To use the twinshare command, activate the virtual environment:"
    print_message "  source venv/bin/activate"
    print_message "Then run:"
    print_message "  twinshare --help"
else
    # Install package system-wide
    print_message "Installing package system-wide..."
    if [ "$EUID" -eq 0 ]; then
        pip3 install -e .
    else
        sudo pip3 install -e .
    fi
    
    # Explicitly install all required dependencies
    print_message "Installing required dependencies..."
    if [ "$EUID" -eq 0 ]; then
        pip3 install pyyaml aiohttp asyncio tabulate cryptography python-daemon netifaces
    else
        sudo pip3 install pyyaml aiohttp asyncio tabulate cryptography python-daemon netifaces
    fi
    
    # Create symlink to the CLI script in /usr/local/bin
    print_message "Creating symlink to the CLI script..."
    if [ -f "/usr/local/bin/twinshare" ]; then
        print_warning "Symlink already exists."
    else
        if [ "$EUID" -eq 0 ]; then
            ln -s "$PROJECT_DIR/bin/twinshare" "/usr/local/bin/twinshare"
            chmod +x "/usr/local/bin/twinshare"
        else
            sudo ln -s "$PROJECT_DIR/bin/twinshare" "/usr/local/bin/twinshare"
            sudo chmod +x "/usr/local/bin/twinshare"
        fi
    fi
    
    print_message "Installation complete!"
    print_message "You can now use the twinshare command:"
    print_message "  twinshare --help"
fi

# Test the installation
print_message "Testing the installation..."
if command -v twinshare &> /dev/null; then
    print_message "twinshare command is available."
    twinshare --help
else
    print_error "twinshare command is not available. Please check the installation."
    exit 1
fi

exit 0
