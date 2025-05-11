# SafetyTwin CLI Usage Examples

This document provides examples of how to use the SafetyTwin CLI for managing virtual machines and P2P networking.

## Installation

First, install the SafetyTwin package:

```bash
cd /path/to/safetytwin/share
pip install -e .
```

This will install the `safetytwin` command-line tool.

## Virtual Machine Management

### List VMs

```bash
safetytwin vm list
```

To get output in JSON format:

```bash
safetytwin vm list --format json
```

### Create a VM

```bash
safetytwin vm create my-vm --image ubuntu-20.04 --cpu 2 --memory 4096 --disk 40
```

### Start a VM

```bash
safetytwin vm start my-vm
```

### Get VM Status

```bash
safetytwin vm status my-vm
```

### Stop a VM

```bash
safetytwin vm stop my-vm
```

To force stop:

```bash
safetytwin vm stop my-vm --force
```

### Delete a VM

```bash
safetytwin vm delete my-vm
```

To keep the disk:

```bash
safetytwin vm delete my-vm --keep-disk
```

## P2P Network Management

### Start P2P Services

```bash
safetytwin p2p start
```

### List Peers

```bash
safetytwin p2p list
```

To get output in JSON format:

```bash
safetytwin p2p list --format json
```

### Send a Message to a Peer

```bash
safetytwin p2p send peer-id message-type '{"key": "value"}'
```

### Stop P2P Services

```bash
safetytwin p2p stop
```

## Remote VM Management

### List Remote VMs

```bash
safetytwin remote vm-list peer-id
```

### Create a Remote VM

```bash
safetytwin remote vm-create peer-id my-vm --image ubuntu-20.04 --cpu 2 --memory 4096 --disk 40
```

### Start a Remote VM

```bash
safetytwin remote vm-start peer-id vm-id
```

### Stop a Remote VM

```bash
safetytwin remote vm-stop peer-id vm-id
```

### Delete a Remote VM

```bash
safetytwin remote vm-delete peer-id vm-id
```

## Advanced Usage

### Debug Mode

To enable debug logging:

```bash
safetytwin --debug vm list
```

### Custom Configuration

To use a custom configuration file:

```bash
safetytwin --config /path/to/config.yaml vm list
```
