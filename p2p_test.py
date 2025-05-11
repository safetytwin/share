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
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

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
    HAVE_DEPENDENCIES = True
except ImportError:
    logger.warning("Optional dependencies (netifaces) not available. Some features will be limited.")
    HAVE_DEPENDENCIES = False

class P2PNode:
    def __init__(self, node_type="server", config_file=None):
        """Initialize a P2P node."""
        # Generate a unique node ID
        self.node_id = str(uuid.uuid4())
        self.node_type = node_type
        self.name = f"twinshare-{node_type}"
        
        # Set up logging
        self.setup_logging()
        
        # Load configuration
        self.load_config(config_file)
        
        # Initialize discovery service
        self.zeroconf = None
        self.browser = None
        self.info = None
        self.running = False
        
        # Initialize peers
        self.peers = {}
        
        # Get IP address
        self.ip_address = self.get_ip_address()
        
        # Log initialization
        logger.info(f"Node initialized: {self.node_id} ({self.name}, {self.ip_address})")
        logger.info(f"Discovery port: {self.discovery_port}, Network port: {self.network_port}")
    
    def setup_logging(self):
        """Set up logging for the node."""
        # Create a logger for the node
        self.logger = logging.getLogger(f"p2p_node_{self.node_id}")
        self.logger.setLevel(logging.INFO)
        
        # Create a file handler for the node
        file_handler = logging.FileHandler(f"logs/p2p_node_{self.node_id}.log")
        file_handler.setLevel(logging.INFO)
        
        # Create a formatter and add it to the file handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the file handler to the logger
        self.logger.addHandler(file_handler)
    
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
    
    def get_ip_address(self):
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
    
    def start_discovery(self):
        """Start the P2P discovery service."""
        if not HAVE_DEPENDENCIES:
            logger.warning("Discovery service not available without zeroconf dependency")
            return False
        
        try:
            # Create a zeroconf instance
            self.zeroconf = Zeroconf()
            
            # Register the service
            self.info = ServiceInfo(
                "_twinshare._udp.local.",
                f"{self.node_id}._twinshare._udp.local.",
                addresses=[socket.inet_aton(self.ip_address)],
                port=self.discovery_port,  # Use discovery_port (UDP) for service registration
                properties={
                    'name': self.name,
                    'node_id': self.node_id,
                    'type': self.node_type,
                    'network_port': str(self.network_port)  # Include network_port in properties
                },
                server=f"{self.name}.local."
            )
            
            try:
                self.zeroconf.register_service(self.info)
                logger.info(f"Registered service: {self.name} on {self.ip_address}:{self.discovery_port}")
            except Exception as e:
                logger.error(f"Failed to register service: {str(e)}")
            
            # Start the browser to discover other services
            self.browser = ServiceBrowser(self.zeroconf, "_twinshare._udp.local.", self)
            
            logger.info(f"Started discovery service on {self.ip_address}:{self.discovery_port} (UDP)")
            logger.info(f"Network service available on {self.ip_address}:{self.network_port} (TCP)")
            
            # Add a manual discovery method for Docker networks
            # This helps when mDNS/Zeroconf doesn't work well in containerized environments
            logger.info("Calling manual peer discovery method")
            self._discover_docker_peers()
            
            # Mark service as running
            self.running = True
            
            return True
        except Exception as e:
            logger.error(f"Failed to start discovery service: {str(e)}")
            return False
    
    def _discover_docker_peers(self):
        """Manually discover peers in Docker network by IP pattern."""
        logger.info("Attempting manual peer discovery for Docker network")
        
        if self.node_type == "server":
            # Server is at 172.30.0.2, client is at 172.30.0.3
            client_ip = "172.30.0.3"
            logger.info(f"Server manually discovering client at {client_ip}")
            self._add_peer("twinshare-client", client_ip, self.network_port)
            
            # Try to ping the client to verify connectivity
            self._verify_peer_connectivity("twinshare-client", client_ip, self.network_port)
        elif self.node_type == "client":
            # Server is at 172.30.0.2
            server_ip = "172.30.0.2"
            logger.info(f"Client manually discovering server at {server_ip}")
            self._add_peer("twinshare-server", server_ip, self.network_port)
            
            # Try to ping the server to verify connectivity
            self._verify_peer_connectivity("twinshare-server", server_ip, self.network_port)
    
    def _verify_peer_connectivity(self, name, ip_address, port):
        """Verify connectivity to a peer by attempting to connect to its TCP port."""
        try:
            logger.info(f"Verifying connectivity to {name} at {ip_address}:{port}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex((ip_address, port))
                if result == 0:
                    logger.info(f"Successfully connected to {name} at {ip_address}:{port}")
                    return True
                else:
                    logger.warning(f"Failed to connect to {name} at {ip_address}:{port}, error code: {result}")
                    return False
        except Exception as e:
            logger.error(f"Error verifying connectivity to {name}: {e}")
            return False
    
    def _add_peer(self, name, ip_address, port):
        """Add a peer to the known peers list."""
        peer_id = f"{name}_{ip_address}_{port}"
        if peer_id not in self.peers:
            self.peers[peer_id] = {
                'name': name,
                'ip': ip_address,
                'port': port,
                'last_seen': time.time()
            }
            logger.info(f"Added peer: {name} at {ip_address}:{port}")
        else:
            # Update last seen time
            self.peers[peer_id]['last_seen'] = time.time()
            logger.info(f"Updated peer: {name} at {ip_address}:{port}")
    
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
                    result = s.connect_ex((peer['ip'], peer['port']))
                    
                    if result == 0:
                        logger.info(f"Ping successful: {peer_id} ({peer['name']}, {peer['ip']}:{peer['port']})")
                        peer['last_seen'] = time.time()
                    else:
                        logger.warning(f"Ping failed: {peer_id} ({peer['name']}, {peer['ip']}:{peer['port']})")
            except Exception as e:
                logger.error(f"Error pinging peer {peer_id}: {e}")

    def remove_service(self, zeroconf, type, name):
        """Remove a service from the list of known peers."""
        logger.info(f"Service removed: {name}")

    def add_service(self, zeroconf, type, name):
        """Add a service to the list of known peers."""
        try:
            info = zeroconf.get_service_info(type, name)
            if info and hasattr(info, 'properties') and b'name' in info.properties and b'node_id' in info.properties:
                peer_name = info.properties.get(b'name', b'unknown').decode()
                peer_id = f"{peer_name}-{info.properties.get(b'node_id', b'unknown').decode()}"
                
                # Get network port from properties or use discovery port as fallback
                network_port = int(info.properties.get(b'network_port', str(info.port).encode()).decode())
                
                if peer_id not in self.peers:
                    self.peers[peer_id] = {
                        'name': peer_name,
                        'ip': socket.inet_ntoa(info.address),
                        'port': network_port,
                        'last_seen': time.time()
                    }
                    logger.info(f"Added peer via Zeroconf: {peer_name} at {socket.inet_ntoa(info.address)}:{network_port}")
        except Exception as e:
            logger.error(f"Error adding service {name}: {e}")

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
    logger.info(f"Starting discovery service for {args.type} node")
    if not node.start_discovery():
        logger.error("Failed to start discovery service")
        return 1
    
    # Create a simple TCP server to listen for connections
    def start_tcp_server():
        try:
            logger.info(f"Starting TCP server on {node.ip_address}:{node.network_port}")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((node.ip_address, node.network_port))
            server_socket.listen(5)
            server_socket.settimeout(1)  # Non-blocking with 1 second timeout
            
            while True:
                try:
                    client, addr = server_socket.accept()
                    logger.info(f"Accepted connection from {addr}")
                    client.send(b"Hello from " + node.name.encode())
                    client.close()
                except socket.timeout:
                    # This is expected, just continue the loop
                    pass
                except Exception as e:
                    logger.error(f"Error in TCP server: {e}")
                
                # Check if we should exit
                if not node.running:
                    break
        except Exception as e:
            logger.error(f"Failed to start TCP server: {e}")
        finally:
            try:
                server_socket.close()
            except:
                pass
    
    # Start TCP server in a separate thread
    import threading
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()
    
    try:
        # Main loop
        while True:
            # Ping peers every 5 seconds
            node.ping_peers()
            
            # Re-discover peers every 30 seconds
            if int(time.time()) % 30 == 0:
                logger.info("Re-discovering peers")
                node._discover_docker_peers()
            
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Stopping P2P test script")
    finally:
        # Stop discovery service
        node.running = False
        node.stop_discovery()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
