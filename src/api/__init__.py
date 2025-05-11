#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł API dla AI Environment Manager.

Zapewnia interfejs API do zarządzania maszynami wirtualnymi, siecią P2P
i innymi zasobami w środowisku AI Environment Manager.
"""

from .p2p_api import P2PAPI
from .vm_api import VMAPI

# Eksportuj klasy API
__all__ = ["VMAPI", "P2PAPI", "API"]


class API:
    """
    Główna klasa API dla AI Environment Manager.

    Zapewnia dostęp do wszystkich funkcji API poprzez jeden interfejs.
    """

    def __init__(self):
        """Inicjalizuje główne API"""
        self.vm = VMAPI()
        self.p2p = P2PAPI()
