#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Główny skrypt wejściowy dla interfejsu wiersza poleceń AI Environment Manager.

Ten skrypt jest punktem wejściowym dla interfejsu wiersza poleceń,
umożliwiając zarządzanie maszynami wirtualnymi, siecią P2P i innymi
zasobami w środowisku AI Environment Manager.
"""

import logging
import os
import sys
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić importowanie modułów
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import commands module directly to avoid circular imports
from src.cli.commands import CLI


def main():
    """
    Funkcja główna dla interfejsu wiersza poleceń.
    """
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
