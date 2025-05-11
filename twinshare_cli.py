#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone entry point for the twinshare CLI.
This script is designed to be installed as a console script entry point
via pip install from PyPI.
"""

import os
import sys
import importlib.util
from pathlib import Path

def is_module_available(module_name):
    """Check if a module can be imported"""
    return importlib.util.find_spec(module_name) is not None

def main():
    """Main entry point for the twinshare CLI"""
    # Add the current directory to the path if needed
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Try different import strategies
    try:
        # First try direct import (works when installed via pip)
        from src.cli.main import main as cli_main
        return cli_main()
    except ImportError:
        # If that fails, try to adjust the path
        try:
            # Add parent directory to path
            parent_dir = str(Path(__file__).resolve().parent)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            # Try import again
            if is_module_available('src.cli.main'):
                from src.cli.main import main as cli_main
                return cli_main()
            else:
                print("Error: Could not import twinshare CLI module.")
                print("Make sure the package is installed correctly.")
                return 1
        except Exception as e:
            print(f"Error starting twinshare CLI: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
