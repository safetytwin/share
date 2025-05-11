#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Główny skrypt wejściowy dla interfejsu wiersza poleceń AI Environment Manager.

Ten skrypt jest punktem wejściowym dla interfejsu wiersza poleceń,
umożliwiając zarządzanie maszynami wirtualnymi, siecią P2P i innymi
zasobami w środowisku AI Environment Manager.
"""

import importlib.util
import logging
import os
import sys
from pathlib import Path


# Funkcja do sprawdzania czy moduł jest dostępny
def is_module_available(module_name):
    return importlib.util.find_spec(module_name) is not None


# Próba bezpośredniego importu
try:
    from src.cli.commands import CLI
except ImportError:
    # Jeśli bezpośredni import nie zadziała, spróbuj dodać katalog nadrzędny do ścieżki
    parent_dir = str(Path(__file__).resolve().parent.parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Sprawdź czy teraz możemy zaimportować moduł
    if is_module_available("src.cli.commands"):
        from src.cli.commands import CLI
    else:
        # Ostatnia próba z relatywnym importem
        try:
            from ..cli.commands import CLI
        except ImportError:
            print("Nie można zaimportować modułu commands. Sprawdź instalację pakietu.")
            sys.exit(1)


def main():
    """
    Funkcja główna dla interfejsu wiersza poleceń.
    """
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
