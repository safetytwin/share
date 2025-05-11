#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Główny skrypt wejściowy dla interfejsu wiersza poleceń AI Environment Manager.

Ten skrypt jest punktem wejściowym dla interfejsu wiersza poleceń,
umożliwiając zarządzanie maszynami wirtualnymi, siecią P2P i innymi
zasobami w środowisku AI Environment Manager.
"""

import os
import sys
import logging
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić importowanie modułów
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.cli.commands import main

if __name__ == "__main__":
    main()
