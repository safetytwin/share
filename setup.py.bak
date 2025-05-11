#!/usr/bin/env python3
# Skrypt instalacyjny
"""
setup.py
"""

from setuptools import setup, find_packages

setup(
    name="twinshare",
    version="0.1.20",
    description="Twin Share - Environment Manager - narzędzie do dzielenia się środowiskami Embedded/AI/VM",
    author="Tom Sapletta",
    packages=find_packages(),
    package_dir={"": "."},
    py_modules=["twinshare_cli"],
    install_requires=[
        "libvirt-python>=8.0.0",
        "aiohttp[speedups]<4.0.0,>=3.8.0",
        "aiohttp-cors>=0.7.0",
        "asyncio>=3.4.3",
        "tabulate>=0.9.0",
        "pyyaml>=6.0",
        "cryptography>=40.0.0",
        "python-daemon>=3.0.0",
        "netifaces>=0.11.0",
        "zeroconf>=0.38.0"
    ],
    entry_points={
        "console_scripts": [
            "twinshare=twinshare_cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    package_data={
        "src": ["**/*.json", "**/*.yaml", "**/*.yml"],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0"
        ],
        "windows": [
            "pywin32>=300"
        ]
    },
    include_package_data=True,
)
