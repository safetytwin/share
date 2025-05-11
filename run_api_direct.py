#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct script to run the REST API server without daemon mode.
This is a simplified version that runs in the foreground.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.api.rest_server import start_server

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    
    # Get host and port from environment or use defaults
    host = os.environ.get("AI_ENV_API_HOST", "0.0.0.0")
    port = int(os.environ.get("AI_ENV_API_PORT", "37780"))
    
    print(f"Starting REST API server on {host}:{port}")
    
    # Start the server
    server = start_server(host=host, port=port)
