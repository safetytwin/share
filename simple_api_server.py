#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple API server starter that doesn't rely on the daemon module.
This runs the API server directly in the foreground.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add the project directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import the API server
from src.api.rest_server import RESTServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("api-server")

async def main():
    """Main function to start the API server"""
    # Get host and port from environment or use defaults
    host = os.environ.get("AI_ENV_API_HOST", "0.0.0.0")
    port = int(os.environ.get("AI_ENV_API_PORT", "37780"))
    
    logger.info(f"Starting REST API server on {host}:{port}")
    
    # Create and start the server
    server = RESTServer(host=host, port=port)
    await server.start()
    
    # Keep the server running
    try:
        logger.info("Server is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
