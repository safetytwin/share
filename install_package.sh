#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print messages
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 is not installed. Attempting to install pip..."
    python3 -m ensurepip --upgrade || {
        print_error "Failed to install pip. Please install pip manually and try again."
        exit 1
    }
fi

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || {
    print_error "Failed to change to project directory."
    exit 1
}

print_message "Installing twinshare package..."

# Create a dedicated virtual environment for twinshare
VENV_DIR="${HOME}/.twinshare_venv"
print_message "Creating virtual environment at ${VENV_DIR}..."

# Check if virtual environment already exists
if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists. Updating it..."
else
    python3 -m venv "$VENV_DIR" || {
        print_error "Failed to create virtual environment. Please install python3-venv package and try again."
        exit 1
    }
    print_success "Virtual environment created successfully."
fi

# Activate the virtual environment
print_message "Activating virtual environment..."
source "${VENV_DIR}/bin/activate" || {
    print_error "Failed to activate virtual environment."
    exit 1
}

# Upgrade pip in the virtual environment
print_message "Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
print_message "Installing package in development mode..."
pip install -e .

# Explicitly install all required dependencies
print_message "Installing required dependencies..."
pip install pyyaml aiohttp asyncio tabulate cryptography python-daemon netifaces zeroconf

# Create the bin directory in the user's home if it doesn't exist
USER_BIN_DIR="${HOME}/.local/bin"
mkdir -p "$USER_BIN_DIR"

# Create a wrapper script that activates the virtual environment and runs twinshare
WRAPPER_SCRIPT="${USER_BIN_DIR}/twinshare"
print_message "Creating wrapper script at ${WRAPPER_SCRIPT}..."

# Store the absolute path to the package directory
ABSOLUTE_PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
VENV_DIR="\${HOME}/.twinshare_venv"
PACKAGE_DIR="$ABSOLUTE_PACKAGE_DIR"

if [ -d "\$VENV_DIR" ]; then
    source "\${VENV_DIR}/bin/activate"
    
    # Run the CLI module directly to avoid circular imports
    PYTHONPATH="\${PACKAGE_DIR}:\${PYTHONPATH}" python -c "import sys; sys.path.insert(0, '\${PACKAGE_DIR}'); from src.cli.main import main; sys.exit(main())" "\$@"
else
    echo "Error: twinshare virtual environment not found. Please reinstall the package."
    exit 1
fi
EOF

chmod +x "$WRAPPER_SCRIPT"

# Add the bin directory to PATH if it's not already there
if [[ ":$PATH:" != *":${USER_BIN_DIR}:"* ]]; then
    print_message "Adding ${USER_BIN_DIR} to PATH in your profile..."
    
    # Determine which shell configuration file to use
    SHELL_CONFIG=""
    if [ -f "${HOME}/.bashrc" ]; then
        SHELL_CONFIG="${HOME}/.bashrc"
    elif [ -f "${HOME}/.zshrc" ]; then
        SHELL_CONFIG="${HOME}/.zshrc"
    elif [ -f "${HOME}/.profile" ]; then
        SHELL_CONFIG="${HOME}/.profile"
    fi
    
    if [ -n "$SHELL_CONFIG" ]; then
        echo "export PATH=\"\${PATH}:${USER_BIN_DIR}\"" >> "$SHELL_CONFIG"
        print_success "Added ${USER_BIN_DIR} to PATH in ${SHELL_CONFIG}"
        print_warning "Please run 'source ${SHELL_CONFIG}' or start a new terminal session to update your PATH."
    else
        print_warning "Could not find a shell configuration file. Please add ${USER_BIN_DIR} to your PATH manually."
    fi
fi

# Test the installation
print_message "Testing the installation..."
if command -v twinshare &> /dev/null; then
    print_success "twinshare command is available in PATH."
else
    print_warning "twinshare command is not available in PATH yet. You can run it using ${WRAPPER_SCRIPT} or add ${USER_BIN_DIR} to your PATH."
fi

print_success "Installation completed successfully!"
print_message "You can now use the 'twinshare' command to run the CLI."
print_message "If the command is not found, you may need to:"
print_message "1. Run 'source ~/.bashrc' (or your shell's config file)"
print_message "2. Start a new terminal session"
print_message "3. Run the command with the full path: ${WRAPPER_SCRIPT}"

# Deactivate the virtual environment
deactivate
