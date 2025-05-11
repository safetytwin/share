#!/bin/bash
# Script to fix the twinshare CLI command without requiring sudo

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

# Get project directory
PROJECT_DIR=$(pwd)
print_message "Project directory: $PROJECT_DIR"

# Create a simple shell script to run the twinshare command
print_message "Creating twinshare command script..."
cat > twinshare << EOF
#!/bin/bash
# Simple wrapper for twinshare command
export PYTHONPATH="$PROJECT_DIR"
python3 -m src.cli.main "\$@"
EOF

# Make it executable
chmod +x twinshare
print_message "Created executable twinshare command in current directory"

# Test the command
print_message "Testing twinshare command..."
./twinshare --help

if [ $? -eq 0 ]; then
    print_message "twinshare command is working!"
    print_message "You can use it with:"
    print_message "    ./twinshare <command>"
    
    # Create symlink in user's bin directory if possible
    if [ -d "$HOME/.local/bin" ]; then
        print_message "Creating symlink in ~/.local/bin..."
        ln -sf "$PROJECT_DIR/twinshare" "$HOME/.local/bin/twinshare"
        print_message "Added symlink to ~/.local/bin/twinshare"
        print_message "Make sure ~/.local/bin is in your PATH"
        print_message "You can now use 'twinshare' command from anywhere"
    else
        print_warning "~/.local/bin directory not found"
        print_message "You can use the command from this directory with ./twinshare"
    fi
else
    print_error "There was an issue with the twinshare command."
    print_message "Check for any error messages above."
fi
