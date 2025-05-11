#!/usr/bin/env python3
"""
Simple P2P networking test script for TwinShare.
This script tests the basic P2P discovery and networking functionality.
"""

import asyncio
import argparse
import logging
import sys
import time
import uuid
import socket
import netifaces
import json
import os
from zeroconf import ServiceInfo, Zeroconf

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/p2p_test.log')
    ]
)
logger = logging.getLogger("p2p_test")

class P2PNode:
    def __init__(self, node_type, node_id=None, config_file=None):
        self.node_type = node_type
        self.node_id = node_id or str(uuid.uuid4())
        self.hostname = socket.gethostname()
        self.discovery_port = 47777
        self.network_port = 47778
        self.zeroconf = None
        self.info = None
        self.peers = {}
        self.running = False
        self.known_servers = []
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        # Get IP address
        self.ip_address = self._get_ip_address()
        logger.info(f"Node initialized: {self.node_id} ({self.hostname}, {self.ip_address})")
    
    def load_config(self, config_file):
        """Load configuration from a JSON file."""
        try:
            logger.info(f"Loading configuration from {config_file}")
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Apply configuration
            if 'node_type' in config:
                self.node_type = config['node_type']
            if 'discovery_port' in config:
                self.discovery_port = config['discovery_port']
            if 'network_port' in config:
                self.network_port = config['network_port']
            if 'known_servers' in config:
                self.known_servers = config['known_servers']
            if 'log_level' in config:
                logging.getLogger().setLevel(getattr(logging, config['log_level']))
            
            logger.info(f"Configuration loaded: {config}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def _get_ip_address(self):
        """Get the IP address of the node."""
        try:
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for address in addresses[netifaces.AF_INET]:
                        if 'addr' in address and address['addr'] != '127.0.0.1':
                            return address['addr']
        except Exception as e:
            logger.error(f"Error getting IP address: {e}")
        
        # Fallback to socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.error(f"Error getting IP address via socket: {e}")
            return "127.0.0.1"
    
    def start_discovery(self):
        """Start the P2P discovery service."""
        try:
            logger.info("Starting P2P discovery service...")
            self.zeroconf = Zeroconf()
            
            # Create service info
            self.info = ServiceInfo(
                "_twinshare._udp.local.",
                f"{self.node_id}._twinshare._udp.local.",
                addresses=[socket.inet_aton(self.ip_address)],
                port=self.discovery_port,
                properties={
                    'node_id': self.node_id.encode('utf-8'),
                    'hostname': self.hostname.encode('utf-8'),
                    'node_type': self.node_type.encode('utf-8'),
                    'network_port': str(self.network_port).encode('utf-8')
                }
            )
            
            # Register service (synchronous)
            self.zeroconf.register_service(self.info)
            self.running = True
            logger.info("P2P discovery service started")
            return True
        except Exception as e:
            logger.error(f"Error starting P2P discovery service: {e}")
            return False
    
    def stop_discovery(self):
        """Stop the P2P discovery service."""
        try:
            if self.zeroconf:
                logger.info("Stopping P2P discovery service...")
                self.zeroconf.unregister_service(self.info)
                self.zeroconf.close()
                self.running = False
                logger.info("P2P discovery service stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping P2P discovery service: {e}")
            return False
    
    def discover_peers(self):
        """Discover peers in the network."""
        # This is a simplified version that would normally use zeroconf browser
        # For testing, we'll add known servers and simulate discovery
        if self.node_type == 'client':
            # Add known servers from configuration
            for server in self.known_servers:
                server_id = f"{server}-node-id"
                if server_id not in self.peers:
                    try:
                        # Try to resolve the hostname
                        ip = socket.gethostbyname(server)
                        self.peers[server_id] = {
                            'node_id': server_id,
                            'hostname': server,
                            'ip': ip,
                            'network_port': 47778,
                            'last_seen': time.time()
                        }
                        logger.info(f"Added known server: {server_id} ({server}, {ip})")
                    except Exception as e:
                        logger.error(f"Error resolving known server {server}: {e}")
            
            # Also add the default server for backward compatibility
            if not self.peers:
                server_id = "server-node-id"
                self.peers[server_id] = {
                    'node_id': server_id,
                    'hostname': 'twinshare-server',
                    'ip': '172.30.0.2',
                    'network_port': 47778,
                    'last_seen': time.time()
                }
                logger.info(f"Added default server: {server_id} (twinshare-server, 172.30.0.2)")
        
        return self.peers
    
    def status(self):
        """Get the status of the P2P node."""
        return {
            'node_id': self.node_id,
            'hostname': self.hostname,
            'ip': self.ip_address,
            'discovery_port': self.discovery_port,
            'network_port': self.network_port,
            'running': self.running,
            'peer_count': len(self.peers),
            'known_servers': self.known_servers
        }
    
    def ping(self, peer_id=None, hostname=None, ip=None):
        """Ping a peer."""
        target = None
        
        # Find the peer
        if peer_id and peer_id in self.peers:
            target = self.peers[peer_id]
        elif hostname:
            for peer in self.peers.values():
                if peer['hostname'] == hostname:
                    target = peer
                    break
        elif ip:
            for peer in self.peers.values():
                if peer['ip'] == ip:
                    target = peer
                    break
        
        if not target:
            if hostname:
                # Try to resolve the hostname and ping it
                try:
                    ip_addr = socket.gethostbyname(hostname)
                    logger.info(f"Resolved {hostname} to {ip_addr}")
                    
                    # Use the actual ping command
                    result = os.system(f"ping -c 1 -W 2 {hostname} > /dev/null 2>&1") == 0
                    logger.info(f"Pinging {hostname} ({ip_addr}): {'Success' if result else 'Failed'}")
                    return result
                except Exception as e:
                    logger.error(f"Error resolving hostname {hostname}: {e}")
                    return False
            elif ip:
                # Use the actual ping command
                result = os.system(f"ping -c 1 -W 2 {ip} > /dev/null 2>&1") == 0
                logger.info(f"Pinging {ip}: {'Success' if result else 'Failed'}")
                return result
            
            logger.error(f"Peer not found: {peer_id or hostname or ip}")
            return False
        
        logger.info(f"Pinging {target['hostname']} ({target['ip']})...")
        # Use the actual ping command
        result = os.system(f"ping -c 1 -W 2 {target['ip']} > /dev/null 2>&1") == 0
        logger.info(f"Ping result: {'Success' if result else 'Failed'}")
        return result

def main():
    parser = argparse.ArgumentParser(description='TwinShare P2P Test')
    parser.add_argument('--type', choices=['server', 'client'], required=True, help='Node type')
    parser.add_argument('--id', help='Node ID (optional)')
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()
    
    # Create node
    node = P2PNode(args.type, args.id, args.config)
    
    # Start discovery
    if not node.start_discovery():
        logger.error("Failed to start P2P discovery service")
        return 1
    
    try:
        # Wait a bit for discovery
        time.sleep(5)
        
        # Show status
        status = node.status()
        logger.info(f"Node status: {status}")
        
        # Discover peers
        peers = node.discover_peers()
        logger.info(f"Discovered peers: {len(peers)}")
        for peer_id, peer in peers.items():
            logger.info(f"  {peer_id}: {peer['hostname']} ({peer['ip']})")
        
        # If client, ping the server
        if args.type == 'client':
            # Ping all known peers
            for peer_id, peer in peers.items():
                # Ping by hostname
                result = node.ping(hostname=peer['hostname'])
                logger.info(f"Ping to {peer['hostname']} by hostname: {'Success' if result else 'Failed'}")
                
                # Ping by IP
                result = node.ping(ip=peer['ip'])
                logger.info(f"Ping to {peer['ip']} by IP: {'Success' if result else 'Failed'}")
        
        # Keep running
        logger.info("Node is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        # Stop discovery
        node.stop_discovery()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
