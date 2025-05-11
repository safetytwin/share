# Skrypt instalacyjny
"""
setup.py
"""

from setuptools import setup, find_packages

setup(
    name="safeytwinshare",
    version="0.1.1",
    description="AI Environment Manager - narzędzie do zarządzania środowiskami AI",
    author="Tom Sapletta",
    packages=find_packages(),
    install_requires=[
        "libvirt-python",
        "aiohttp",
        "asyncio",
        "tabulate",
        "pyyaml",
        "cryptography",
        "python-daemon",
        "netifaces"
    ],
    entry_points={
        "console_scripts": [
            "safetytwin=src.cli.main:main",
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
)
