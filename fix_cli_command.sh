#!/bin/bash
# Script to fix the twinshare CLI command

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

# Get the virtual environment path
VENV_PATH="$(pwd)/venv"
print_message "Using virtual environment at: $VENV_PATH"

# Create a wrapper script for the twinshare command
print_message "Creating twinshare command wrapper..."
cat > $VENV_PATH/bin/twinshare << EOF
#!/bin/bash
# Wrapper script for twinshare command
PYTHONPATH="\$(dirname "\$(dirname "\$(realpath "\$0")")")" \
"\$(dirname "\$(realpath "\$0")")/python3" -m src.cli.main "\$@"
EOF

# Make the wrapper executable
chmod +x $VENV_PATH/bin/twinshare
print_message "Made twinshare command executable"

# Verify the command works
print_message "Testing twinshare command..."
$VENV_PATH/bin/twinshare --help

if [ $? -eq 0 ]; then
    print_message "twinshare command is now working!"
    print_message "To use it, make sure to activate your virtual environment:"
    print_message "    source venv/bin/activate"
    print_message "Then you can run:"
    print_message "    twinshare <command>"
else
    print_error "There was an issue setting up the twinshare command."
    print_message "Try running the API directly with:"
    print_message "    python -m src.cli.main api start"
fi

# Create a symlink to the system bin directory (optional)
if [ -d "$HOME/.local/bin" ]; then
    print_message "Creating symlink in ~/.local/bin for system-wide access..."
    ln -sf $VENV_PATH/bin/twinshare $HOME/.local/bin/twinshare
    print_message "Added symlink to ~/.local/bin/twinshare"
    print_message "Make sure ~/.local/bin is in your PATH"
fi
