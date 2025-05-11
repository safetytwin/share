#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł klienta REST API dla AI Environment Manager.

Zapewnia klienta REST API do zarządzania maszynami wirtualnymi, siecią P2P
i innymi zasobami w środowisku AI Environment Manager.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import aiohttp

logger = logging.getLogger("ai-env-manager.api.rest_client")


class RESTClient:
    """
    Klasa implementująca klienta REST API.

    Zapewnia metody do zarządzania maszynami wirtualnymi, siecią P2P
    i innymi zasobami w środowisku AI Environment Manager poprzez REST API.
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Inicjalizuje klienta REST API.

        Args:
            base_url: Bazowy URL serwera REST API
        """
        self.base_url = base_url.rstrip("/")
        self.session = None

    async def __aenter__(self):
        """
        Inicjalizuje sesję HTTP przy wejściu do kontekstu.

        Returns:
            RESTClient: Instancja klienta REST API
        """
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Zamyka sesję HTTP przy wyjściu z kontekstu.

        Args:
            exc_type: Typ wyjątku
            exc_val: Wartość wyjątku
            exc_tb: Traceback wyjątku
        """
        if self.session:
            await self.session.close()
            self.session = None

    async def _ensure_session(self):
        """
        Zapewnia, że sesja HTTP jest zainicjalizowana.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """
        Wykonuje żądanie GET do serwera REST API.

        Args:
            endpoint: Endpoint API

        Returns:
            Dict[str, Any]: Odpowiedź z serwera REST API

        Raises:
            Exception: Jeśli wystąpi błąd podczas wykonywania żądania
        """
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"

        async with self.session.get(url) as response:
            if response.status >= 400:
                error_data = await response.json()
                raise Exception(
                    f"HTTP Error {response.status}: {error_data.get('error', 'Unknown error')}"
                )

            return await response.json()

    async def _post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wykonuje żądanie POST do serwera REST API.

        Args:
            endpoint: Endpoint API
            data: Dane do wysłania

        Returns:
            Dict[str, Any]: Odpowiedź z serwera REST API

        Raises:
            Exception: Jeśli wystąpi błąd podczas wykonywania żądania
        """
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"

        async with self.session.post(url, json=data) as response:
            if response.status >= 400:
                error_data = await response.json()
                raise Exception(
                    f"HTTP Error {response.status}: {error_data.get('error', 'Unknown error')}"
                )

            return await response.json()

    async def _delete(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wykonuje żądanie DELETE do serwera REST API.

        Args:
            endpoint: Endpoint API
            data: Dane do wysłania

        Returns:
            Dict[str, Any]: Odpowiedź z serwera REST API

        Raises:
            Exception: Jeśli wystąpi błąd podczas wykonywania żądania
        """
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"

        async with self.session.delete(url, json=data) as response:
            if response.status >= 400:
                error_data = await response.json()
                raise Exception(
                    f"HTTP Error {response.status}: {error_data.get('error', 'Unknown error')}"
                )

            return await response.json()

    # Metody VM

    async def list_vms(self) -> List[Dict[str, Any]]:
        """
        Listuje dostępne maszyny wirtualne.

        Returns:
            List[Dict[str, Any]]: Lista maszyn wirtualnych
        """
        response = await self._get("/api/vm")
        return response.get("vms", [])

    async def create_vm(
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
        data = {
            "name": name,
            "image": image,
            "cpu_cores": cpu_cores,
            "memory": memory,
            "disk_size": disk_size,
            "network": network,
            "hypervisor": hypervisor,
        }

        return await self._post("/api/vm", data)

    async def get_vm_status(self, name: str) -> Dict[str, Any]:
        """
        Pobiera status maszyny wirtualnej.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            Dict[str, Any]: Status maszyny wirtualnej
        """
        return await self._get(f"/api/vm/{name}")

    async def start_vm(self, name: str) -> Dict[str, Any]:
        """
        Uruchamia maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            Dict[str, Any]: Wynik operacji
        """
        return await self._post(f"/api/vm/{name}/start")

    async def stop_vm(self, name: str, force: bool = False) -> Dict[str, Any]:
        """
        Zatrzymuje maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            force: Czy wymusić zatrzymanie

        Returns:
            Dict[str, Any]: Wynik operacji
        """
        data = {"force": force}
        return await self._post(f"/api/vm/{name}/stop", data)

    async def delete_vm(self, name: str, delete_disk: bool = True) -> Dict[str, Any]:
        """
        Usuwa maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            delete_disk: Czy usunąć dysk

        Returns:
            Dict[str, Any]: Wynik operacji
        """
        data = {"delete_disk": delete_disk}
        return await self._delete(f"/api/vm/{name}", data)

    # Metody P2P

    async def get_peers(self) -> List[Dict[str, Any]]:
        """
        Pobiera listę węzłów w sieci P2P.

        Returns:
            List[Dict[str, Any]]: Lista węzłów
        """
        response = await self._get("/api/p2p/peers")
        return response.get("peers", [])

    async def get_local_peer_info(self) -> Dict[str, Any]:
        """
        Pobiera informacje o lokalnym węźle P2P.

        Returns:
            Dict[str, Any]: Informacje o lokalnym węźle
        """
        return await self._get("/api/p2p/info")

    async def start_p2p_services(self) -> Dict[str, Any]:
        """
        Uruchamia usługi P2P.

        Returns:
            Dict[str, Any]: Wynik operacji
        """
        return await self._post("/api/p2p/start")

    async def stop_p2p_services(self) -> Dict[str, Any]:
        """
        Zatrzymuje usługi P2P.

        Returns:
            Dict[str, Any]: Wynik operacji
        """
        return await self._post("/api/p2p/stop")

    async def send_message(
        self, peer_id: str, message_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Wysyła wiadomość do węzła.

        Args:
            peer_id: Identyfikator węzła docelowego
            message_type: Typ wiadomości
            data: Dane wiadomości

        Returns:
            Dict[str, Any]: Odpowiedź z węzła docelowego
        """
        request_data = {"peer_id": peer_id, "message_type": message_type, "data": data}

        response = await self._post("/api/p2p/message", request_data)
        return response.get("response", {})

    # Metody zdalnego zarządzania

    async def list_remote_vms(self, peer_id: str) -> List[Dict[str, Any]]:
        """
        Listuje zdalne maszyny wirtualne.

        Args:
            peer_id: Identyfikator węzła docelowego

        Returns:
            List[Dict[str, Any]]: Lista zdalnych maszyn wirtualnych
        """
        response = await self._get(f"/api/remote/{peer_id}/vm")
        return response.get("vms", [])

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
        data = {
            "name": name,
            "image": image,
            "cpu_cores": cpu_cores,
            "memory": memory,
            "disk_size": disk_size,
            "network": network,
            "hypervisor": hypervisor,
        }

        return await self._post(f"/api/remote/{peer_id}/vm", data)

    async def start_remote_vm(self, peer_id: str, vm_id: str) -> Dict[str, Any]:
        """
        Uruchamia zdalną maszynę wirtualną.

        Args:
            peer_id: Identyfikator węzła docelowego
            vm_id: Identyfikator maszyny wirtualnej

        Returns:
            Dict[str, Any]: Odpowiedź z węzła docelowego
        """
        return await self._post(f"/api/remote/{peer_id}/vm/{vm_id}/start")

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
        data = {"force": force}
        return await self._post(f"/api/remote/{peer_id}/vm/{vm_id}/stop", data)

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
        data = {"delete_disk": delete_disk}
        return await self._delete(f"/api/remote/{peer_id}/vm/{vm_id}", data)
