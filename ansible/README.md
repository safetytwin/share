# TwinShare P2P Testing with Ansible

This directory contains Ansible configuration for testing the P2P networking functionality of TwinShare.

## Overview

The Ansible configuration is designed to work with the Docker containers created by Terraform. It:

1. Configures the P2P nodes with appropriate settings
2. Verifies P2P connectivity between nodes
3. Collects and displays test results

## Structure

- `inventory.yml`: Defines the server and client node groups
- `playbook.yml`: Contains tasks for configuring nodes and running tests

## Prerequisites

- Ansible (>= 2.9)
- Docker containers created by Terraform

## Usage

To run the Ansible playbook:

```bash
cd ansible
ansible-playbook -i inventory.yml playbook.yml
```

## Playbook Tasks

The playbook includes several tasks:

1. **Setup TwinShare P2P Test Environment**: Installs dependencies and checks service status
2. **Configure Server Node**: Creates server-specific configuration
3. **Configure Client Node**: Creates client-specific configuration with known servers
4. **Run P2P Tests**: Tests connectivity between nodes and collects results

## Integration with Terraform

This Ansible setup is designed to work with the Terraform configuration in the `../terraform` directory. The Terraform configuration creates the Docker containers that Ansible then configures and tests.

## Automated Testing

For automated testing, use the `../run_terraform_ansible_test.sh` script, which:

1. Applies the Terraform configuration
2. Runs the Ansible playbooks
3. Collects and displays test results
