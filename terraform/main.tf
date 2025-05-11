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
  name     = "twinshare-server"
  hostname = "twinshare-server"
  image    = docker_image.twinshare_test.image_id
  
  # Fix the command to not include the script path
  command = ["--type", "server"]
  
  env = ["PYTHONUNBUFFERED=1"]
  
  networks_advanced {
    name         = docker_network.p2p_network.name
    ipv4_address = "172.30.0.2"
  }
  
  ports {
    internal = 47777
    external = 47777
    protocol = "udp"
    ip       = "0.0.0.0"
  }
  
  ports {
    internal = 47778
    external = 47778
    protocol = "tcp"
    ip       = "0.0.0.0"
  }
}

# Create client container
resource "docker_container" "twinshare_client" {
  name     = "twinshare-client"
  hostname = "twinshare-client"
  image    = docker_image.twinshare_test.image_id
  
  # Fix the command to not include the script path
  command = ["--type", "client"]
  
  env = ["PYTHONUNBUFFERED=1"]
  
  networks_advanced {
    name         = docker_network.p2p_network.name
    ipv4_address = "172.30.0.3"
  }
  
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
