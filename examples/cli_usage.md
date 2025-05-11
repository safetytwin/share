# twinshare CLI Usage Examples

This document provides examples of how to use the twinshare CLI for managing virtual machines and P2P networking.

## Installation

First, install the twinshare package:

```bash
cd /path/to/twinshare/share
pip install -e .
```

This will install the `twinshare` command-line tool.

## Virtual Machine Management

### List VMs

```bash
twinshare vm list
```

To get output in JSON format:

```bash
twinshare vm list --format json
```

### Create a VM

```bash
twinshare vm create my-vm --image ubuntu-20.04 --cpu 2 --memory 4096 --disk 40
```

### Start a VM

```bash
twinshare vm start my-vm
```

### Get VM Status

```bash
twinshare vm status my-vm
```

### Stop a VM

```bash
twinshare vm stop my-vm
```

To force stop:

```bash
twinshare vm stop my-vm --force
```

### Delete a VM

```bash
twinshare vm delete my-vm
```

To keep the disk:

```bash
twinshare vm delete my-vm --keep-disk
```

## P2P Network Management

### Start P2P Services

```bash
twinshare p2p start
```

### List Peers

```bash
twinshare p2p list
```

To get output in JSON format:

```bash
twinshare p2p list --format json
```

### Send a Message to a Peer

```bash
twinshare p2p send peer-id message-type '{"key": "value"}'
```

### Stop P2P Services

```bash
twinshare p2p stop
```

## Remote VM Management

### List Remote VMs

```bash
twinshare remote vm-list peer-id
```

### Create a Remote VM

```bash
twinshare remote vm-create peer-id my-vm --image ubuntu-20.04 --cpu 2 --memory 4096 --disk 40
```

### Start a Remote VM

```bash
twinshare remote vm-start peer-id vm-id
```

### Stop a Remote VM

```bash
twinshare remote vm-stop peer-id vm-id
```

### Delete a Remote VM

```bash
twinshare remote vm-delete peer-id vm-id
```

## Advanced Usage

### Debug Mode

To enable debug logging:

```bash
twinshare --debug vm list
```

### Custom Configuration

To use a custom configuration file:

```bash
twinshare --config /path/to/config.yaml vm list
```
