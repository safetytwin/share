#!/bin/bash
# twinshare Installation Script
# This script installs all necessary dependencies for the twinshare project

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default options
INTERACTIVE=true
SKIP_SYSTEM_DEPS=false
SKIP_SERVICE_INSTALL=false

# Print colored message
print_message() {
    echo -e "${GREEN}[twinshare Installer]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --non-interactive       Run in non-interactive mode"
    echo "  --skip-system-deps      Skip system dependencies installation"
    echo "  --skip-service-install  Skip REST API service installation"
    echo "  --help                  Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --skip-system-deps   # Skip system dependencies installation"
    echo ""
}

# Parse command line arguments
parse_args() {
    for arg in "$@"; do
        case $arg in
            --non-interactive)
                INTERACTIVE=false
                shift
                ;;
            --skip-system-deps)
                SKIP_SYSTEM_DEPS=true
                shift
                ;;
            --skip-service-install)
                SKIP_SERVICE_INSTALL=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $arg"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Check if running with sudo privileges
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        if $INTERACTIVE; then
            print_warning "This script requires sudo privileges for system-level installations."
            print_message "You will be prompted for your password during execution."
            # Just a test sudo to prompt for password once
            sudo true
        else
            print_error "This script requires sudo privileges for system-level installations."
            print_message "Please run with sudo or use the following options:"
            print_message "  --skip-system-deps      Skip system dependencies installation"
            print_message "  --skip-service-install  Skip REST API service installation"
            exit 1
        fi
    fi
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
        print_message "Detected distribution: $DISTRO $VERSION"
    else
        print_warning "Could not detect Linux distribution. Assuming Debian/Ubuntu-based system."
        DISTRO="debian"
    fi
}

# Install system dependencies based on distribution
install_system_dependencies() {
    if $SKIP_SYSTEM_DEPS; then
        print_message "Skipping system dependencies installation as requested."
        return
    fi

    print_message "Installing system dependencies..."
    
    case $DISTRO in
        ubuntu|debian|pop|mint|elementary)
            sudo apt-get update
            sudo apt-get install -y \
                python3 \
                python3-pip \
                python3-venv \
                libvirt-dev \
                pkg-config \
                libvirt-daemon \
                libvirt-daemon-system \
                qemu-kvm \
                bridge-utils \
                virtinst \
                libvirt-clients \
                build-essential \
                python3-dev
            ;;
        fedora|centos|rhel|rocky|alma)
            sudo dnf update -y
            sudo dnf install -y \
                python3 \
                python3-pip \
                python3-virtualenv \
                libvirt-devel \
                pkgconfig \
                libvirt \
                libvirt-daemon-kvm \
                qemu-kvm \
                bridge-utils \
                virt-install \
                libvirt-client \
                gcc \
                python3-devel
            ;;
        arch|manjaro)
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm \
                python \
                python-pip \
                python-virtualenv \
                libvirt \
                pkgconf \
                qemu-desktop \
                bridge-utils \
                virt-install \
                gcc \
                python-setuptools
            ;;
        opensuse|suse)
            sudo zypper refresh
            sudo zypper install -y \
                python3 \
                python3-pip \
                python3-virtualenv \
                libvirt-devel \
                pkg-config \
                libvirt \
                qemu-kvm \
                bridge-utils \
                virt-install \
                gcc \
                python3-devel
            ;;
        *)
            print_error "Unsupported distribution: $DISTRO"
            print_message "Please install the following packages manually:"
            echo "- Python 3 and pip"
            echo "- libvirt development libraries"
            echo "- QEMU/KVM virtualization packages"
            echo "- Build tools (gcc, etc.)"
            exit 1
            ;;
    esac
    
    print_message "System dependencies installed successfully."
}

# Setup Python virtual environment
setup_virtualenv() {
    print_message "Setting up Python virtual environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_message "Virtual environment created."
    else
        print_message "Virtual environment already exists."
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_message "Virtual environment setup complete."
}

# Install Python dependencies
install_python_dependencies() {
    print_message "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        # Activate virtual environment
        source "$SCRIPT_DIR/venv/bin/activate"
        
        # Install dependencies
        pip install -r requirements.txt
        
        # Ensure critical packages are installed with correct versions
        pip install python-daemon
        pip install "aiohttp[speedups]<4.0.0,>=3.8.0"
        pip install aiohttp-cors>=0.7.0
        
        # Deactivate virtual environment
        deactivate
        
        print_message "Python dependencies installed successfully."
    else
        print_error "requirements.txt not found."
        exit 1
    fi
}

# Configure libvirt for the current user
configure_libvirt() {
    if $SKIP_SYSTEM_DEPS; then
        print_message "Skipping libvirt configuration as system dependencies were skipped."
        return
    fi

    print_message "Configuring libvirt for current user..."
    
    # Add current user to libvirt group
    if getent group libvirt > /dev/null; then
        sudo usermod -a -G libvirt $USER
        print_message "Added $USER to libvirt group."
    else
        print_warning "libvirt group not found. Skipping user group configuration."
    fi
    
    # Ensure libvirtd is running
    if command -v systemctl > /dev/null; then
        sudo systemctl enable libvirtd
        sudo systemctl start libvirtd
        print_message "Enabled and started libvirtd service."
    else
        print_warning "systemctl not found. Please ensure libvirtd service is running."
    fi
    
    print_message "libvirt configuration complete."
}

# Install REST API as a system service
install_rest_api_service() {
    if $SKIP_SERVICE_INSTALL; then
        print_message "Skipping REST API service installation as requested."
        print_message "You can start the REST API manually with: python3 scripts/start_rest_api.py start"
        return
    fi

    print_message "Installing REST API service..."
    
    if command -v systemctl > /dev/null; then
        # Create required directories
        print_message "Creating required directories..."
        sudo mkdir -p /var/log/twinshare /var/run/twinshare
        sudo chown $USER:$USER /var/log/twinshare /var/run/twinshare
        print_message "Directories created and permissions set."
        
        # Copy and customize service file
        print_message "Customizing service file for user $USER..."
        # Create a temporary service file with the current user and absolute paths
        cat "$SCRIPT_DIR/scripts/twinshare-rest-api.service" | \
            sed "s/\$USER/$USER/g" | \
            sed "s|/home/tom/github/twinshare/share|$SCRIPT_DIR|g" | \
            sed "s|WorkingDirectory=.*|WorkingDirectory=$SCRIPT_DIR|g" | \
            sed "s|Environment=.*|Environment=\"PYTHONPATH=$SCRIPT_DIR\"|g" | \
            sed "s|/home/tom/github/twinshare/share/venv/bin/python3|$SCRIPT_DIR/venv/bin/python3|g" > /tmp/twinshare-rest-api.service
        
        sudo cp /tmp/twinshare-rest-api.service /etc/systemd/system/twinshare-rest-api.service
        rm /tmp/twinshare-rest-api.service
        
        # Reload systemd
        sudo systemctl daemon-reload
        
        # Enable and start the service
        sudo systemctl enable twinshare-rest-api
        sudo systemctl start twinshare-rest-api
        status=$?
        if [ $status -ne 0 ]; then
            print_warning "Failed to start the service. Check logs with: sudo journalctl -u twinshare-rest-api"
        else
            print_message "REST API service installed and started."
        fi
        
        print_message "You can check its status with: sudo systemctl status twinshare-rest-api"
        print_message "To view logs: sudo journalctl -u twinshare-rest-api"
    else
        print_warning "systemctl not found. Skipping REST API service installation."
        print_message "You can start the REST API manually with:"
        echo "source venv/bin/activate && python scripts/start_rest_api.py start"
    fi
}

# Main installation process
main() {
    print_message "Starting twinshare installation..."
    
    # Get script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR"
    
    # Check sudo access if needed
    if ! $SKIP_SYSTEM_DEPS || ! $SKIP_SERVICE_INSTALL; then
        check_sudo
    fi
    
    # Detect distribution
    detect_distro
    
    # Install system dependencies
    install_system_dependencies
    
    # Setup Python virtual environment
    setup_virtualenv
    
    # Install Python dependencies
    install_python_dependencies
    
    # Configure libvirt
    configure_libvirt
    
    # Install REST API service
    install_rest_api_service
    
    print_message "Installation complete!"
    
    if getent group libvirt > /dev/null; then
        print_message "Please log out and log back in for group changes to take effect."
    fi
    
    print_message "To activate the virtual environment, run: source venv/bin/activate"
}

# Parse command line arguments
parse_args "$@"

# Run the main function
main
