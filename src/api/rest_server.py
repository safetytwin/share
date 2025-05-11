#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł serwera REST API dla AI Environment Manager.

Zapewnia interfejs REST API do zarządzania maszynami wirtualnymi, siecią P2P
i innymi zasobami w środowisku AI Environment Manager.
"""

import asyncio
import json
import logging
import os
from functools import wraps
from typing import Any, Dict, List, Optional, Union

from aiohttp import web
from aiohttp.web import Request, Response, json_response

from ..core.config import config
from . import API

logger = logging.getLogger("ai-env-manager.api.rest")


def json_error(status_code: int, message: str) -> Response:
    """
    Tworzy odpowiedź błędu w formacie JSON.

    Args:
        status_code: Kod statusu HTTP
        message: Komunikat błędu

    Returns:
        Response: Odpowiedź HTTP
    """
    return json_response({"error": message}, status=status_code)


def require_json(f):
    """
    Dekorator wymagający, aby żądanie zawierało dane JSON.

    Args:
        f: Funkcja do udekorowania

    Returns:
        Funkcja udekorowana
    """

    @wraps(f)
    async def wrapper(request: Request) -> Response:
        try:
            await request.json()
        except json.JSONDecodeError:
            return json_error(400, "Invalid JSON")
        return await f(request)

    return wrapper


class RESTServer:
    """
    Klasa implementująca serwer REST API.

    Zapewnia endpointy HTTP do zarządzania maszynami wirtualnymi, siecią P2P
    i innymi zasobami w środowisku AI Environment Manager.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Inicjalizuje serwer REST API.

        Args:
            host: Adres hosta
            port: Port
        """
        self.host = host
        self.port = port
        self.app = web.Application()
        self.api = API()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Konfiguruje trasy API."""
        # Główna trasa
        self.app.router.add_get("/", self.handle_root)

        # Trasy VM
        self.app.router.add_get("/api/vm", self.handle_vm_list)
        self.app.router.add_post("/api/vm", self.handle_vm_create)
        self.app.router.add_get("/api/vm/{name}", self.handle_vm_info)
        self.app.router.add_post("/api/vm/{name}/start", self.handle_vm_start)
        self.app.router.add_post("/api/vm/{name}/stop", self.handle_vm_stop)
        self.app.router.add_delete("/api/vm/{name}", self.handle_vm_delete)

        # Trasy P2P
        self.app.router.add_get("/api/p2p/peers", self.handle_p2p_peers)
        self.app.router.add_get("/api/p2p/info", self.handle_p2p_info)
        self.app.router.add_post("/api/p2p/start", self.handle_p2p_start)
        self.app.router.add_post("/api/p2p/stop", self.handle_p2p_stop)
        self.app.router.add_post("/api/p2p/message", self.handle_p2p_send_message)

        # Trasy zdalnego zarządzania
        self.app.router.add_get("/api/remote/{peer_id}/vm", self.handle_remote_vm_list)
        self.app.router.add_post(
            "/api/remote/{peer_id}/vm", self.handle_remote_vm_create
        )
        self.app.router.add_post(
            "/api/remote/{peer_id}/vm/{vm_id}/start", self.handle_remote_vm_start
        )
        self.app.router.add_post(
            "/api/remote/{peer_id}/vm/{vm_id}/stop", self.handle_remote_vm_stop
        )
        self.app.router.add_delete(
            "/api/remote/{peer_id}/vm/{vm_id}", self.handle_remote_vm_delete
        )

        # Trasy udostępniania workspace'ów
        self.app.router.add_get("/shared", self.handle_shared_list)
        self.app.router.add_post("/shared/{workspace_name}", self.handle_shared_update)
        self.app.router.add_delete(
            "/shared/{workspace_name}", self.handle_shared_delete
        )

    async def handle_root(self, request: Request) -> Response:
        """
        Obsługuje żądanie do głównej trasy.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        return json_response(
            {
                "name": "AI Environment Manager API",
                "version": "0.1.0",
                "endpoints": ["/api/vm", "/api/p2p", "/api/remote"],
            }
        )

    # Handlery VM

    async def handle_vm_list(self, request: Request) -> Response:
        """
        Obsługuje żądanie listowania maszyn wirtualnych.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            vms = self.api.vm.list_vms()
            return json_response({"vms": vms})
        except Exception as e:
            logger.error(f"Error listing VMs: {e}")
            return json_error(500, str(e))

    @require_json
    async def handle_vm_create(self, request: Request) -> Response:
        """
        Obsługuje żądanie tworzenia maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            data = await request.json()

            # Wymagane pola
            required_fields = ["name", "image"]
            for field in required_fields:
                if field not in data:
                    return json_error(400, f"Missing required field: {field}")

            # Opcjonalne pola
            cpu_cores = data.get("cpu_cores", 2)
            memory = data.get("memory", 2048)
            disk_size = data.get("disk_size", 20)
            network = data.get("network", "default")
            hypervisor = data.get("hypervisor", "kvm")

            # Utwórz VM
            result = self.api.vm.create_vm(
                name=data["name"],
                image=data["image"],
                cpu_cores=cpu_cores,
                memory=memory,
                disk_size=disk_size,
                network=network,
                hypervisor=hypervisor,
            )

            return json_response(result)
        except Exception as e:
            logger.error(f"Error creating VM: {e}")
            return json_error(500, str(e))

    async def handle_vm_info(self, request: Request) -> Response:
        """
        Obsługuje żądanie informacji o maszynie wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            name = request.match_info["name"]
            status = self.api.vm.get_vm_status(name)
            return json_response(status)
        except Exception as e:
            logger.error(f"Error getting VM info: {e}")
            return json_error(404, str(e))

    async def handle_vm_start(self, request: Request) -> Response:
        """
        Obsługuje żądanie uruchomienia maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            name = request.match_info["name"]
            result = self.api.vm.start_vm(name)
            return json_response({"success": result})
        except Exception as e:
            logger.error(f"Error starting VM: {e}")
            return json_error(500, str(e))

    async def handle_vm_stop(self, request: Request) -> Response:
        """
        Obsługuje żądanie zatrzymania maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            name = request.match_info["name"]

            # Sprawdź, czy żądanie zawiera dane JSON
            force = False
            try:
                data = await request.json()
                force = data.get("force", False)
            except json.JSONDecodeError:
                # Brak danych JSON, używamy domyślnych wartości
                pass

            result = self.api.vm.stop_vm(name, force=force)
            return json_response({"success": result})
        except Exception as e:
            logger.error(f"Error stopping VM: {e}")
            return json_error(500, str(e))

    async def handle_vm_delete(self, request: Request) -> Response:
        """
        Obsługuje żądanie usunięcia maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            name = request.match_info["name"]

            # Sprawdź, czy żądanie zawiera dane JSON
            delete_disk = True
            try:
                data = await request.json()
                delete_disk = data.get("delete_disk", True)
            except json.JSONDecodeError:
                # Brak danych JSON, używamy domyślnych wartości
                pass

            result = self.api.vm.delete_vm(name, delete_disk=delete_disk)
            return json_response({"success": result})
        except Exception as e:
            logger.error(f"Error deleting VM: {e}")
            return json_error(500, str(e))

    # Handlery P2P

    async def handle_p2p_peers(self, request: Request) -> Response:
        """
        Obsługuje żądanie listowania węzłów P2P.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            peers = self.api.p2p.get_peers()
            return json_response({"peers": peers})
        except Exception as e:
            logger.error(f"Error listing P2P peers: {e}")
            return json_error(500, str(e))

    async def handle_p2p_info(self, request: Request) -> Response:
        """
        Obsługuje żądanie informacji o lokalnym węźle P2P.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            info = self.api.p2p.get_local_peer_info()
            return json_response(info)
        except Exception as e:
            logger.error(f"Error getting P2P info: {e}")
            return json_error(500, str(e))

    async def handle_p2p_start(self, request: Request) -> Response:
        """
        Obsługuje żądanie uruchomienia usług P2P.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            result = await self.api.p2p.start_services()
            return json_response({"success": result})
        except Exception as e:
            logger.error(f"Error starting P2P services: {e}")
            return json_error(500, str(e))

    async def handle_p2p_stop(self, request: Request) -> Response:
        """
        Obsługuje żądanie zatrzymania usług P2P.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            result = await self.api.p2p.stop_services()
            return json_response({"success": result})
        except Exception as e:
            logger.error(f"Error stopping P2P services: {e}")
            return json_error(500, str(e))

    @require_json
    async def handle_p2p_send_message(self, request: Request) -> Response:
        """
        Obsługuje żądanie wysłania wiadomości P2P.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            data = await request.json()

            # Wymagane pola
            required_fields = ["peer_id", "message_type", "data"]
            for field in required_fields:
                if field not in data:
                    return json_error(400, f"Missing required field: {field}")

            # Wyślij wiadomość
            response = await self.api.p2p.send_message(
                peer_id=data["peer_id"],
                message_type=data["message_type"],
                data=data["data"],
            )

            return json_response({"response": response})
        except Exception as e:
            logger.error(f"Error sending P2P message: {e}")
            return json_error(500, str(e))

    # Handlery zdalnego zarządzania

    async def handle_remote_vm_list(self, request: Request) -> Response:
        """
        Obsługuje żądanie listowania zdalnych maszyn wirtualnych.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            peer_id = request.match_info["peer_id"]
            vms = await self.api.vm.list_remote_vms(peer_id)
            return json_response({"vms": vms})
        except Exception as e:
            logger.error(f"Error listing remote VMs: {e}")
            return json_error(500, str(e))

    @require_json
    async def handle_remote_vm_create(self, request: Request) -> Response:
        """
        Obsługuje żądanie tworzenia zdalnej maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            peer_id = request.match_info["peer_id"]
            data = await request.json()

            # Wymagane pola
            required_fields = ["name", "image"]
            for field in required_fields:
                if field not in data:
                    return json_error(400, f"Missing required field: {field}")

            # Opcjonalne pola
            cpu_cores = data.get("cpu_cores", 2)
            memory = data.get("memory", 2048)
            disk_size = data.get("disk_size", 20)
            network = data.get("network", "default")
            hypervisor = data.get("hypervisor", "kvm")

            # Utwórz zdalną VM
            result = await self.api.vm.create_remote_vm(
                peer_id=peer_id,
                name=data["name"],
                image=data["image"],
                cpu_cores=cpu_cores,
                memory=memory,
                disk_size=disk_size,
                network=network,
                hypervisor=hypervisor,
            )

            return json_response(result)
        except Exception as e:
            logger.error(f"Error creating remote VM: {e}")
            return json_error(500, str(e))

    async def handle_remote_vm_start(self, request: Request) -> Response:
        """
        Obsługuje żądanie uruchomienia zdalnej maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            peer_id = request.match_info["peer_id"]
            vm_id = request.match_info["vm_id"]

            result = await self.api.vm.start_remote_vm(peer_id, vm_id)
            return json_response(result)
        except Exception as e:
            logger.error(f"Error starting remote VM: {e}")
            return json_error(500, str(e))

    async def handle_remote_vm_stop(self, request: Request) -> Response:
        """
        Obsługuje żądanie zatrzymania zdalnej maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            peer_id = request.match_info["peer_id"]
            vm_id = request.match_info["vm_id"]

            # Sprawdź, czy żądanie zawiera dane JSON
            force = False
            try:
                data = await request.json()
                force = data.get("force", False)
            except json.JSONDecodeError:
                # Brak danych JSON, używamy domyślnych wartości
                pass

            result = await self.api.vm.stop_remote_vm(peer_id, vm_id, force=force)
            return json_response(result)
        except Exception as e:
            logger.error(f"Error stopping remote VM: {e}")
            return json_error(500, str(e))

    async def handle_remote_vm_delete(self, request: Request) -> Response:
        """
        Obsługuje żądanie usunięcia zdalnej maszyny wirtualnej.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            peer_id = request.match_info["peer_id"]
            vm_id = request.match_info["vm_id"]

            # Sprawdź, czy żądanie zawiera dane JSON
            delete_disk = True
            try:
                data = await request.json()
                delete_disk = data.get("delete_disk", True)
            except json.JSONDecodeError:
                # Brak danych JSON, używamy domyślnych wartości
                pass

            result = await self.api.vm.delete_remote_vm(
                peer_id, vm_id, delete_disk=delete_disk
            )
            return json_response(result)
        except Exception as e:
            logger.error(f"Error deleting remote VM: {e}")
            return json_error(500, str(e))

    # Handlery udostępniania workspace'ów

    async def handle_shared_list(self, request: Request) -> Response:
        """
        Obsługuje żądanie listowania udostępnionych workspace'ów.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            # W rzeczywistej implementacji, pobierz listę udostępnionych workspace'ów
            # Na razie zwracamy pustą listę
            shared_workspaces = []
            return json_response({"shared_workspaces": shared_workspaces})
        except Exception as e:
            logger.error(f"Błąd podczas listowania udostępnionych workspace'ów: {e}")
            return json_error(
                500, f"Błąd podczas listowania udostępnionych workspace'ów: {e}"
            )

    @require_json
    async def handle_shared_update(self, request: Request) -> Response:
        """
        Obsługuje żądanie aktualizacji udostępnienia workspace'a.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            workspace_name = request.match_info["workspace_name"]
            data = await request.json()

            if "enable" not in data:
                return json_error(400, "Brak wymaganego pola 'enable'")

            enable = data["enable"]

            # W rzeczywistej implementacji, aktualizuj status udostępnienia workspace'a
            # Na razie tylko logujemy akcję
            action = "udostępniono" if enable else "wyłączono udostępnianie"
            logger.info(f"Workspace '{workspace_name}' {action}")

            return json_response(
                {"success": True, "workspace": workspace_name, "shared": enable}
            )
        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji udostępnienia workspace'a: {e}")
            return json_error(
                500, f"Błąd podczas aktualizacji udostępnienia workspace'a: {e}"
            )

    async def handle_shared_delete(self, request: Request) -> Response:
        """
        Obsługuje żądanie usunięcia udostępnienia workspace'a.

        Args:
            request: Żądanie HTTP

        Returns:
            Response: Odpowiedź HTTP
        """
        try:
            workspace_name = request.match_info["workspace_name"]

            # W rzeczywistej implementacji, usuń udostępnienie workspace'a
            # Na razie tylko logujemy akcję
            logger.info(f"Usunięto udostępnienie workspace'a '{workspace_name}'")

            return json_response(
                {"success": True, "workspace": workspace_name, "shared": False}
            )
        except Exception as e:
            logger.error(f"Błąd podczas usuwania udostępnienia workspace'a: {e}")
            return json_error(
                500, f"Błąd podczas usuwania udostępnienia workspace'a: {e}"
            )

    async def start(self) -> None:
        """Uruchamia serwer REST API."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"REST API server started at http://{self.host}:{self.port}")

        # Zachowaj referencje do runner i site, aby można było je później zatrzymać
        self.runner = runner
        self.site = site

    async def stop(self) -> None:
        """Zatrzymuje serwer REST API."""
        await self.runner.cleanup()
        logger.info("REST API server stopped")


async def start_server(host: str = "0.0.0.0", port: int = 8080) -> RESTServer:
    """
    Uruchamia serwer REST API.

    Args:
        host: Adres hosta
        port: Port

    Returns:
        RESTServer: Instancja serwera REST API
    """
    server = RESTServer(host, port)
    await server.start()
    return server


if __name__ == "__main__":
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Uruchom serwer
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(start_server())

    try:
        # Utrzymuj serwer działający
        loop.run_forever()
    except KeyboardInterrupt:
        # Zatrzymaj serwer po naciśnięciu Ctrl+C
        loop.run_until_complete(server.stop())
    finally:
        loop.close()
