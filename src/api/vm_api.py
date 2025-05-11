#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł API dla zarządzania maszynami wirtualnymi.

Zapewnia interfejs API do zarządzania maszynami wirtualnymi,
umożliwiając integrację z innymi aplikacjami.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from ..p2p.discovery import discovery
from ..p2p.network import network
from ..p2p.protocol import (
    Message,
    VMCreateMessage,
    VMDeleteMessage,
    VMInfoMessage,
    VMListMessage,
    VMStartMessage,
    VMStatusMessage,
    VMStopMessage,
)
from ..runtime.vm import VMRuntime

logger = logging.getLogger("ai-env-manager.api.vm")


class VMAPI:
    """
    Klasa implementująca API do zarządzania maszynami wirtualnymi.

    Zapewnia metody do tworzenia, uruchamiania, zatrzymywania, usuwania
    i listowania maszyn wirtualnych, zarówno lokalnie, jak i zdalnie.
    """

    def __init__(self):
        """Inicjalizuje API maszyn wirtualnych"""
        self.vm_runtime = VMRuntime()

    # Lokalne operacje VM

    def list_vms(self) -> List[Dict[str, Any]]:
        """
        Listuje dostępne maszyny wirtualne.

        Returns:
            List[Dict[str, Any]]: Lista maszyn wirtualnych
        """
        return self.vm_runtime.list_vms()

    def create_vm(
        self,
        name: str,
        image: str,
        cpu_cores: int = 2,
        memory: int = 2048,
        disk_size: int = 20,
        network: str = "default",
        hypervisor: str = "kvm",
    ) -> Dict[str, Any]:
        """
        Tworzy nową maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            image: Obraz bazowy do użycia
            cpu_cores: Liczba rdzeni CPU
            memory: Ilość pamięci RAM w MB
            disk_size: Rozmiar dysku w GB
            network: Nazwa sieci
            hypervisor: Typ hypervisora (kvm, virtualbox)

        Returns:
            Dict[str, Any]: Informacje o utworzonej maszynie wirtualnej
        """
        return self.vm_runtime.create_vm(
            name=name,
            image=image,
            cpu_cores=cpu_cores,
            memory=memory,
            disk_size=disk_size,
            network=network,
            hypervisor=hypervisor,
        )

    def start_vm(self, name: str) -> bool:
        """
        Uruchamia maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            bool: Czy operacja się powiodła
        """
        return self.vm_runtime.start_vm(name)

    def stop_vm(self, name: str, force: bool = False) -> bool:
        """
        Zatrzymuje maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            force: Czy wymusić zatrzymanie

        Returns:
            bool: Czy operacja się powiodła
        """
        return self.vm_runtime.stop_vm(name, force=force)

    def delete_vm(self, name: str, delete_disk: bool = True) -> bool:
        """
        Usuwa maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            delete_disk: Czy usunąć dysk

        Returns:
            bool: Czy operacja się powiodła
        """
        return self.vm_runtime.delete_vm(name, delete_disk=delete_disk)

    def get_vm_status(self, name: str) -> Dict[str, Any]:
        """
        Pobiera status maszyny wirtualnej.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            Dict[str, Any]: Status maszyny wirtualnej
        """
        return self.vm_runtime.get_vm_status(name)

    # Zdalne operacje VM

    async def list_remote_vms(self, peer_id: str) -> List[Dict[str, Any]]:
        """
        Listuje zdalne maszyny wirtualne.

        Args:
            peer_id: Identyfikator węzła docelowego

        Returns:
            List[Dict[str, Any]]: Lista zdalnych maszyn wirtualnych
        """
        # Utwórz wiadomość
        message = VMListMessage(sender_id=discovery.peer_id, receiver_id=peer_id)

        # Wyślij wiadomość
        response = await network.send_message(
            peer_id=peer_id, message_type=message.type, data=message.data
        )

        if response and "vms" in response:
            return response["vms"]

        return []

    async def create_remote_vm(
        self,
        peer_id: str,
        name: str,
        image: str,
        cpu_cores: int = 2,
        memory: int = 2048,
        disk_size: int = 20,
        network: str = "default",
        hypervisor: str = "kvm",
    ) -> Dict[str, Any]:
        """
        Tworzy zdalną maszynę wirtualną.

        Args:
            peer_id: Identyfikator węzła docelowego
            name: Nazwa maszyny wirtualnej
            image: Obraz bazowy do użycia
            cpu_cores: Liczba rdzeni CPU
            memory: Ilość pamięci RAM w MB
            disk_size: Rozmiar dysku w GB
            network: Nazwa sieci
            hypervisor: Typ hypervisora (kvm, virtualbox)

        Returns:
            Dict[str, Any]: Odpowiedź z węzła docelowego
        """
        # Utwórz wiadomość
        message = VMCreateMessage(
            name=name,
            image=image,
            cpu_cores=cpu_cores,
            memory=memory,
            disk_size=disk_size,
            network=network,
            hypervisor=hypervisor,
            sender_id=discovery.peer_id,
            receiver_id=peer_id,
        )

        # Wyślij wiadomość
        response = await network.send_message(
            peer_id=peer_id, message_type=message.type, data=message.data
        )

        return response or {}

    async def start_remote_vm(self, peer_id: str, vm_id: str) -> Dict[str, Any]:
        """
        Uruchamia zdalną maszynę wirtualną.

        Args:
            peer_id: Identyfikator węzła docelowego
            vm_id: Identyfikator maszyny wirtualnej

        Returns:
            Dict[str, Any]: Odpowiedź z węzła docelowego
        """
        # Utwórz wiadomość
        message = VMStartMessage(
            vm_id=vm_id, sender_id=discovery.peer_id, receiver_id=peer_id
        )

        # Wyślij wiadomość
        response = await network.send_message(
            peer_id=peer_id, message_type=message.type, data=message.data
        )

        return response or {}

    async def stop_remote_vm(
        self, peer_id: str, vm_id: str, force: bool = False
    ) -> Dict[str, Any]:
        """
        Zatrzymuje zdalną maszynę wirtualną.

        Args:
            peer_id: Identyfikator węzła docelowego
            vm_id: Identyfikator maszyny wirtualnej
            force: Czy wymusić zatrzymanie

        Returns:
            Dict[str, Any]: Odpowiedź z węzła docelowego
        """
        # Utwórz wiadomość
        message = VMStopMessage(
            vm_id=vm_id, force=force, sender_id=discovery.peer_id, receiver_id=peer_id
        )

        # Wyślij wiadomość
        response = await network.send_message(
            peer_id=peer_id, message_type=message.type, data=message.data
        )

        return response or {}

    async def delete_remote_vm(
        self, peer_id: str, vm_id: str, delete_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Usuwa zdalną maszynę wirtualną.

        Args:
            peer_id: Identyfikator węzła docelowego
            vm_id: Identyfikator maszyny wirtualnej
            delete_disk: Czy usunąć dysk

        Returns:
            Dict[str, Any]: Odpowiedź z węzła docelowego
        """
        # Utwórz wiadomość
        message = VMDeleteMessage(
            vm_id=vm_id,
            delete_disk=delete_disk,
            sender_id=discovery.peer_id,
            receiver_id=peer_id,
        )

        # Wyślij wiadomość
        response = await network.send_message(
            peer_id=peer_id, message_type=message.type, data=message.data
        )

        return response or {}

    async def get_remote_vm_status(self, peer_id: str, vm_id: str) -> Dict[str, Any]:
        """
        Pobiera status zdalnej maszyny wirtualnej.

        Args:
            peer_id: Identyfikator węzła docelowego
            vm_id: Identyfikator maszyny wirtualnej

        Returns:
            Dict[str, Any]: Status zdalnej maszyny wirtualnej
        """
        # Utwórz wiadomość
        message = VMStatusMessage(
            vm_id=vm_id, sender_id=discovery.peer_id, receiver_id=peer_id
        )

        # Wyślij wiadomość
        response = await network.send_message(
            peer_id=peer_id, message_type=message.type, data=message.data
        )

        return response or {}
