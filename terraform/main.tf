terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# Create a custom network
resource "docker_network" "p2p_network" {
  name = "p2p_test_network"
  driver = "bridge"
  ipam_config {
    subnet = "172.30.0.0/16"  # Changed subnet to avoid conflicts
  }
}

# Create server container
resource "docker_container" "twinshare_server" {
  name  = "twinshare-server"
  image = docker_image.twinshare_test.name
  hostname = "twinshare-server"
  
  networks_advanced {
    name = docker_network.p2p_network.name
    ipv4_address = "172.30.0.2"  # Updated IP to match new subnet
  }
  
  ports {
    internal = 37777
    external = 47777  # Changed from 37777 to 47777
    protocol = "udp"
  }
  
  ports {
    internal = 37778
    external = 47778  # Changed from 37778 to 47778
  }
  
  command = ["/app/p2p_test.py", "--type", "server"]
  
  env = [
    "PYTHONUNBUFFERED=1"
  ]
}

# Create client container
resource "docker_container" "twinshare_client" {
  name  = "twinshare-client"
  image = docker_image.twinshare_test.name
  hostname = "twinshare-client"
  
  networks_advanced {
    name = docker_network.p2p_network.name
    ipv4_address = "172.30.0.3"  # Updated IP to match new subnet
  }
  
  command = ["/app/p2p_test.py", "--type", "client"]
  
  env = [
    "PYTHONUNBUFFERED=1"
  ]
  
  depends_on = [
    docker_container.twinshare_server
  ]
}

# Build the Docker image
resource "docker_image" "twinshare_test" {
  name = "twinshare-p2p-test:latest"
  build {
    context = ".."
    dockerfile = "../Dockerfile.p2ptest"
  }
}

# Output the container IDs
output "server_container_id" {
  value = docker_container.twinshare_server.id
}

output "client_container_id" {
  value = docker_container.twinshare_client.id
}
