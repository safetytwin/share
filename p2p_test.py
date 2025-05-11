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
import json
import os

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

# Try to import optional dependencies
try:
    import netifaces
    from zeroconf import ServiceInfo, Zeroconf
    HAVE_DEPENDENCIES = True
except ImportError:
    logger.warning("Optional dependencies (netifaces, zeroconf) not available. Some features will be limited.")
    HAVE_DEPENDENCIES = False

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
    
    def _get_ip_address(self):
        """Get the IP address of the current machine."""
        if not HAVE_DEPENDENCIES:
            return "127.0.0.1"  # Fallback when netifaces is not available
            
        try:
            # Try to get the IP address from a network interface
            for interface in netifaces.interfaces():
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for address in addresses[netifaces.AF_INET]:
                        ip = address['addr']
                        # Skip localhost
                        if ip != '127.0.0.1':
                            return ip
            
            # Fallback to localhost if no other IP is found
            return '127.0.0.1'
        except Exception as e:
            logger.error(f"Error getting IP address: {e}")
            return '127.0.0.1'
    
    def load_config(self, config_file):
        """Load configuration from a JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update node configuration
            if 'node_type' in config:
                self.node_type = config['node_type']
            if 'discovery_port' in config:
                self.discovery_port = config['discovery_port']
            if 'network_port' in config:
                self.network_port = config['network_port']
            if 'known_servers' in config:
                self.known_servers = config['known_servers']
            
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def start_discovery(self):
        """Start the P2P discovery service."""
        if not HAVE_DEPENDENCIES:
            logger.warning("Discovery service not available without zeroconf dependency")
            return False
            
        try:
            if self.running:
                logger.warning("Discovery service already running")
                return True
            
            # Create Zeroconf instance
            self.zeroconf = Zeroconf()
            
            # Create service info
            self.info = ServiceInfo(
                "_twinshare._tcp.local.",
                f"{self.node_id}._twinshare._tcp.local.",
                addresses=[socket.inet_aton(self.ip_address)],
                port=self.network_port,
                properties={
                    'node_type': self.node_type,
                    'hostname': self.hostname
                }
            )
            
            # Register service
            self.zeroconf.register_service(self.info)
            self.running = True
            logger.info(f"Started discovery service on {self.ip_address}:{self.discovery_port}")
            
            # If this is a client, connect to known servers
            if self.node_type == "client" and self.known_servers:
                self._connect_to_known_servers()
            
            return True
        except Exception as e:
            logger.error(f"Error starting discovery service: {e}")
            return False
    
    def _connect_to_known_servers(self):
        """Connect to known servers."""
        logger.info(f"Connecting to known servers: {self.known_servers}")
        
        for server in self.known_servers:
            try:
                # Try to resolve hostname to IP
                try:
                    ip = socket.gethostbyname(server)
                except socket.gaierror:
                    # If hostname resolution fails, try to use it as an IP
                    ip = server
                
                # Generate a server ID
                server_id = f"server-{uuid.uuid4()}"
                
                # Add server to peers
                self.peers[server_id] = {
                    'node_id': server_id,
                    'hostname': server,
                    'ip': ip,
                    'network_port': 47778,
                    'last_seen': time.time()
                }
                logger.info(f"Added known server: {server_id} ({server}, {ip})")
            except Exception as e:
                logger.error(f"Error connecting to server {server}: {e}")
        
        # If no servers were added, add a default server
        if not self.peers:
            server_id = f"server-{uuid.uuid4()}"
            self.peers[server_id] = {
                'node_id': server_id,
                'hostname': 'twinshare-server',
                'ip': '172.30.0.2',
                'network_port': 47778,
                'last_seen': time.time()
            }
            logger.info(f"Added default server: {server_id} (twinshare-server, 172.30.0.2)")
    
    def stop_discovery(self):
        """Stop the P2P discovery service."""
        if not HAVE_DEPENDENCIES:
            logger.warning("Discovery service not available without zeroconf dependency")
            return
            
        try:
            if not self.running:
                logger.warning("Discovery service not running")
                return
            
            # Unregister service
            if self.zeroconf and self.info:
                self.zeroconf.unregister_service(self.info)
                self.zeroconf.close()
            
            self.running = False
            logger.info("Stopped discovery service")
        except Exception as e:
            logger.error(f"Error stopping discovery service: {e}")
    
    def ping_peers(self):
        """Ping all known peers to check connectivity."""
        if not self.peers:
            logger.warning("No peers to ping")
            return
        
        logger.info(f"Pinging {len(self.peers)} peers")
        
        for peer_id, peer in list(self.peers.items()):
            try:
                # Create a socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # Set a timeout
                    s.settimeout(2)
                    
                    # Try to connect to the peer
                    result = s.connect_ex((peer['ip'], peer['network_port']))
                    
                    if result == 0:
                        logger.info(f"Ping successful: {peer_id} ({peer['hostname']}, {peer['ip']}:{peer['network_port']})")
                        peer['last_seen'] = time.time()
                    else:
                        logger.warning(f"Ping failed: {peer_id} ({peer['hostname']}, {peer['ip']}:{peer['network_port']})")
            except Exception as e:
                logger.error(f"Error pinging peer {peer_id}: {e}")

def main():
    """Main function for the P2P test script."""
    parser = argparse.ArgumentParser(description='P2P Test Script')
    parser.add_argument('--type', choices=['server', 'client'], default='server',
                        help='Node type (server or client)')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    args = parser.parse_args()
    
    # Create P2P node
    node = P2PNode(args.type, config_file=args.config)
    
    # Start discovery service
    if not node.start_discovery():
        logger.error("Failed to start discovery service")
        return 1
    
    try:
        # Main loop
        while True:
            # Ping peers every 5 seconds
            node.ping_peers()
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Stopping P2P test script")
    finally:
        # Stop discovery service
        node.stop_discovery()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
