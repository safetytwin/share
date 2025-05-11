FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libvirt-dev \
    libvirt-clients \
    qemu-kvm \
    openssh-client \
    curl \
    netcat-openbsd \
    iproute2 \
    iputils-ping \
    net-tools \
    gcc \
    python3-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . /app/

# Install the package
RUN pip install -e .

# Create data directory
RUN mkdir -p /data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Copy the entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose ports
EXPOSE 37777/udp 37778 37780

ENTRYPOINT ["docker-entrypoint.sh"]
