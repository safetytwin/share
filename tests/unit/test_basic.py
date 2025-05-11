#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic unit tests for Twin Share
"""

import os
import sys
import unittest

# Add the project root directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class TestBasic(unittest.TestCase):
    """Basic test cases."""

    def test_module_structure(self):
        """Test that the module structure exists."""
        src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
        
        # Check that src directory exists
        self.assertTrue(os.path.exists(src_dir), "src directory not found")
        
        # Check that key module directories exist
        self.assertTrue(os.path.exists(os.path.join(src_dir, "api")), "api module directory not found")
        self.assertTrue(os.path.exists(os.path.join(src_dir, "p2p")), "p2p module directory not found")
        
        # Check for key files
        self.assertTrue(os.path.exists(os.path.join(src_dir, "api", "rest_server.py")), 
                        "rest_server.py not found")
        self.assertTrue(os.path.exists(os.path.join(src_dir, "p2p", "network.py")), 
                        "network.py not found")

    def test_environment(self):
        """Test that the environment is set up correctly."""
        # Check for project structure
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.assertTrue(
            os.path.exists(os.path.join(project_root, "requirements.txt")),
            "requirements.txt not found"
        )
        self.assertTrue(
            os.path.exists(os.path.join(project_root, "pyproject.toml")),
            "pyproject.toml not found"
        )


if __name__ == "__main__":
    unittest.main()
