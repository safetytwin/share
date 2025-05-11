# Skrypt instalacyjny
"""
setup.py
"""

from setuptools import setup, find_packages

setup(
    name="twinshare",
    version="0.1.14",
    description="Twin Share - Environment Manager - narzędzie do dzielenia się środowiskami Embedded/AI/VM",
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
    scripts=["bin/twinshare"],
    entry_points={
        "console_scripts": [
            "twinshare=src.cli.main:main",
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
