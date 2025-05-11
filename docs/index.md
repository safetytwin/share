# TwinShare Documentation

Welcome to the TwinShare documentation. This guide provides comprehensive information about installing, configuring, and using the TwinShare system for managing virtual machines and containers in a P2P network environment.

## Documentation Sections

### Getting Started
- [Installation Guide](installation.md) - How to install TwinShare on your system
- [Service Installation](service_installation.md) - Setting up TwinShare as a system service
- [User Guide](user_guide.md) - Basic usage instructions for TwinShare

### Features & Functionality
- [VM Sharing Guide](vm_sharing_guide.md) - How to share and manage virtual machines
- [REST API Guide](rest_api_guide.md) - Using the TwinShare REST API
- [Example: VM Sharing](example_vm_sharing.md) - Step-by-step example of VM sharing

### Technical Documentation
- [Architecture Overview](architecture.md) - System architecture and design principles
- [Modules Documentation](modules.md) - Description of TwinShare modules
- [API Reference](api_reference.md) - Detailed API documentation
- [P2P Networking](p2p_networking.md) - How the P2P networking functionality works

### For Developers
- [Developer Guide](developer_guide.md) - Guide for developers contributing to TwinShare
- [Testing](tests.md) - Information about the test suite and how to run tests

### Support
- [Troubleshooting](troubleshooting.md) - Common issues and their solutions

## Recent Updates

- **P2P Node Discovery Enhancement**: Improved P2P discovery to support peer lookups by hostname and IP address
- **Remote VM Management**: Added comprehensive remote VM management capabilities
- **REST API Improvements**: Enhanced REST API for better VM and container management

## Quick Start

```bash
# Install TwinShare
pip install twinshare

# Start the P2P network
twinshare p2p start

# List local VMs
twinshare vm list

# List remote VMs
twinshare remote vm-list --peer hostname
```

For more detailed instructions, please refer to the [User Guide](user_guide.md).
