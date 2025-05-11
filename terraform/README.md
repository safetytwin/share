# TwinShare P2P Testing with Terraform and Ansible

This directory contains Terraform configuration for setting up a P2P testing environment for TwinShare.

## Overview

The Terraform configuration creates a Docker-based testing environment with two containers:
- `twinshare-server`: Acts as the P2P server node
- `twinshare-client`: Acts as the P2P client node that connects to the server

Both containers run our custom P2P test script that simulates the P2P networking functionality of TwinShare.

## Prerequisites

- Terraform (>= 1.0.0)
- Docker
- Docker provider for Terraform

## Usage

To apply the Terraform configuration:

```bash
cd terraform
terraform init
terraform apply
```

To destroy the infrastructure:

```bash
terraform destroy
```

## Configuration

The main Terraform configuration is in `main.tf`. It defines:

- A Docker network with a specific subnet
- Two Docker containers with fixed IP addresses
- Port mappings for P2P discovery and communication
- Container environment variables

## Integration with Ansible

This Terraform setup is designed to work with the Ansible playbooks in the `../ansible` directory. After applying the Terraform configuration, you can run the Ansible playbooks to configure and test the P2P functionality.

## Automated Testing

For automated testing, use the `../run_terraform_ansible_test.sh` script, which:

1. Applies the Terraform configuration
2. Runs the Ansible playbooks
3. Collects and displays test results
