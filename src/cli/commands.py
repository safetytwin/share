#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł komend CLI dla AI Environment Manager.

Implementuje komendy wiersza poleceń do zarządzania maszynami wirtualnymi,
kontenerami i innymi zasobami w środowisku AI Environment Manager.
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from tabulate import tabulate

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić importowanie modułów
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.api.rest_server import start_server
from src.core.config import Config, config
from src.core.workspace import Workspace
from src.p2p.discovery import discovery
from src.p2p.network import network
from src.p2p.protocol import (
    Message,
    VMCreateMessage,
    VMDeleteMessage,
    VMInfoMessage,
    VMListMessage,
    VMStartMessage,
    VMStatusMessage,
    VMStopMessage,
)
from src.runtime.vm import VMRuntime

logger = logging.getLogger("ai-env-manager.cli")


class CLI:
    """
    Klasa implementująca interfejs wiersza poleceń.

    Zapewnia komendy do zarządzania maszynami wirtualnymi, kontenerami
    i innymi zasobami w środowisku AI Environment Manager.
    """

    def __init__(self):
        """Inicjalizuje interfejs wiersza poleceń"""
        self.vm_runtime = VMRuntime()
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """
        Tworzy parser argumentów wiersza poleceń.

        Returns:
            argparse.ArgumentParser: Parser argumentów
        """
        # Główny parser
        parser = argparse.ArgumentParser(
            description="AI Environment Manager - narzędzie do zarządzania środowiskami AI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.add_argument(
            "--debug", action="store_true", help="Włącza tryb debugowania"
        )

        parser.add_argument(
            "--config", type=str, help="Ścieżka do pliku konfiguracyjnego"
        )

        # Podparsery dla różnych komend
        subparsers = parser.add_subparsers(
            dest="command", title="Dostępne komendy", help="Komenda do wykonania"
        )

        # Komenda: vm
        vm_parser = subparsers.add_parser(
            "vm", help="Zarządzanie maszynami wirtualnymi"
        )

        vm_subparsers = vm_parser.add_subparsers(
            dest="vm_command", title="Komendy VM", help="Komenda VM do wykonania"
        )

        # Komenda: vm list
        vm_list_parser = vm_subparsers.add_parser(
            "list", help="Listuje dostępne maszyny wirtualne"
        )

        vm_list_parser.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Format wyjścia (domyślnie: table)",
        )

        # Komenda: vm create
        vm_create_parser = vm_subparsers.add_parser(
            "create", help="Tworzy nową maszynę wirtualną"
        )

        vm_create_parser.add_argument("name", type=str, help="Nazwa maszyny wirtualnej")

        vm_create_parser.add_argument(
            "--image", type=str, required=True, help="Obraz bazowy do użycia"
        )

        vm_create_parser.add_argument(
            "--cpu", type=int, default=2, help="Liczba rdzeni CPU (domyślnie: 2)"
        )

        vm_create_parser.add_argument(
            "--memory",
            type=int,
            default=2048,
            help="Ilość pamięci RAM w MB (domyślnie: 2048)",
        )

        vm_create_parser.add_argument(
            "--disk", type=int, default=20, help="Rozmiar dysku w GB (domyślnie: 20)"
        )

        vm_create_parser.add_argument(
            "--network",
            type=str,
            default="default",
            help="Nazwa sieci (domyślnie: default)",
        )

        vm_create_parser.add_argument(
            "--hypervisor",
            type=str,
            choices=["kvm", "virtualbox"],
            default="kvm",
            help="Typ hypervisora (domyślnie: kvm)",
        )

        # Komenda: vm start
        vm_start_parser = vm_subparsers.add_parser(
            "start", help="Uruchamia maszynę wirtualną"
        )

        vm_start_parser.add_argument("name", type=str, help="Nazwa maszyny wirtualnej")

        # Komenda: vm stop
        vm_stop_parser = vm_subparsers.add_parser(
            "stop", help="Zatrzymuje maszynę wirtualną"
        )

        vm_stop_parser.add_argument("name", type=str, help="Nazwa maszyny wirtualnej")

        vm_stop_parser.add_argument(
            "--force",
            action="store_true",
            help="Wymusza zatrzymanie maszyny wirtualnej",
        )

        # Komenda: vm delete
        vm_delete_parser = vm_subparsers.add_parser(
            "delete", help="Usuwa maszynę wirtualną"
        )

        vm_delete_parser.add_argument("name", type=str, help="Nazwa maszyny wirtualnej")

        vm_delete_parser.add_argument(
            "--keep-disk", action="store_true", help="Zachowuje dysk maszyny wirtualnej"
        )

        # Komenda: vm status
        vm_status_parser = vm_subparsers.add_parser(
            "status", help="Pobiera status maszyny wirtualnej"
        )

        vm_status_parser.add_argument("name", type=str, help="Nazwa maszyny wirtualnej")

        # Komenda: p2p
        p2p_parser = subparsers.add_parser("p2p", help="Zarządzanie siecią P2P")

        p2p_subparsers = p2p_parser.add_subparsers(
            dest="p2p_command", title="Komendy P2P", help="Komenda P2P do wykonania"
        )

        # Komenda: p2p start
        p2p_start_parser = p2p_subparsers.add_parser(
            "start", help="Uruchamia usługi P2P"
        )

        # Komenda: p2p stop
        p2p_stop_parser = p2p_subparsers.add_parser(
            "stop", help="Zatrzymuje usługi P2P"
        )

        # Komenda: p2p status
        p2p_status_parser = p2p_subparsers.add_parser(
            "status", help="Wyświetla status usług P2P"
        )

        # Komenda: p2p list
        p2p_list_parser = p2p_subparsers.add_parser(
            "list", help="Listuje węzły w sieci P2P"
        )

        p2p_list_parser.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Format wyjścia (domyślnie: table)",
        )

        # Komenda: p2p send
        p2p_send_parser = p2p_subparsers.add_parser(
            "send", help="Wysyła wiadomość do węzła P2P"
        )

        p2p_send_parser.add_argument(
            "peer_id", type=str, help="Identyfikator węzła docelowego"
        )

        p2p_send_parser.add_argument("message_type", type=str, help="Typ wiadomości")

        p2p_send_parser.add_argument(
            "data", type=str, help="Dane wiadomości w formacie JSON"
        )

        # Komenda: remote
        remote_parser = subparsers.add_parser(
            "remote", help="Zdalne zarządzanie maszynami wirtualnymi"
        )

        remote_subparsers = remote_parser.add_subparsers(
            dest="remote_command",
            title="Komendy zdalne",
            help="Komenda zdalna do wykonania",
        )

        # Komenda: remote vm-list
        remote_vm_list_parser = remote_subparsers.add_parser(
            "vm-list", help="Listuje zdalne maszyny wirtualne"
        )

        remote_vm_list_parser.add_argument(
            "--peer", type=str, required=True, help="Adres węzła docelowego"
        )

        remote_vm_list_parser.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Format wyjścia (domyślnie: table)",
        )

        # Komenda: remote vm-create
        remote_vm_create_parser = remote_subparsers.add_parser(
            "vm-create", help="Tworzy zdalną maszynę wirtualną"
        )

        remote_vm_create_parser.add_argument(
            "--peer", type=str, required=True, help="Adres węzła docelowego"
        )

        remote_vm_create_parser.add_argument(
            "name", type=str, help="Nazwa maszyny wirtualnej"
        )

        remote_vm_create_parser.add_argument(
            "--image", type=str, required=True, help="Obraz bazowy do użycia"
        )

        remote_vm_create_parser.add_argument(
            "--cpu", type=int, default=2, help="Liczba rdzeni CPU (domyślnie: 2)"
        )

        remote_vm_create_parser.add_argument(
            "--memory",
            type=int,
            default=2048,
            help="Ilość pamięci RAM w MB (domyślnie: 2048)",
        )

        remote_vm_create_parser.add_argument(
            "--disk", type=int, default=20, help="Rozmiar dysku w GB (domyślnie: 20)"
        )

        # Komenda: remote vm-start
        remote_vm_start_parser = remote_subparsers.add_parser(
            "vm-start", help="Uruchamia zdalną maszynę wirtualną"
        )

        remote_vm_start_parser.add_argument(
            "--peer", type=str, required=True, help="Adres węzła docelowego"
        )

        remote_vm_start_parser.add_argument(
            "vm_id", type=str, help="Identyfikator maszyny wirtualnej"
        )

        # Komenda: remote vm-stop
        remote_vm_stop_parser = remote_subparsers.add_parser(
            "vm-stop", help="Zatrzymuje zdalną maszynę wirtualną"
        )

        remote_vm_stop_parser.add_argument(
            "--peer", type=str, required=True, help="Adres węzła docelowego"
        )

        remote_vm_stop_parser.add_argument(
            "vm_id", type=str, help="Identyfikator maszyny wirtualnej"
        )

        remote_vm_stop_parser.add_argument(
            "--force",
            action="store_true",
            help="Wymusza zatrzymanie maszyny wirtualnej",
        )

        # Komenda: remote vm-delete
        remote_vm_delete_parser = remote_subparsers.add_parser(
            "vm-delete", help="Usuwa zdalną maszynę wirtualną"
        )

        remote_vm_delete_parser.add_argument(
            "--peer", type=str, required=True, help="Adres węzła docelowego"
        )

        remote_vm_delete_parser.add_argument(
            "vm_id", type=str, help="Identyfikator maszyny wirtualnej"
        )

        remote_vm_delete_parser.add_argument(
            "--keep-disk", action="store_true", help="Zachowuje dysk maszyny wirtualnej"
        )

        # Komenda: workspace
        workspace_parser = subparsers.add_parser(
            "workspace", help="Zarządzanie przestrzeniami roboczymi"
        )

        workspace_subparsers = workspace_parser.add_subparsers(
            dest="workspace_command",
            title="Komendy Workspace",
            help="Komenda Workspace do wykonania",
        )

        # Komenda: workspace list
        workspace_list_parser = workspace_subparsers.add_parser(
            "list", help="Listuje dostępne przestrzenie robocze"
        )

        workspace_list_parser.add_argument(
            "--format",
            choices=["table", "json", "yaml"],
            default="table",
            help="Format wyjścia (domyślnie: table)",
        )

        # Komenda: workspace share
        workspace_share_parser = workspace_subparsers.add_parser(
            "share", help="Udostępnia przestrzeń roboczą"
        )

        workspace_share_parser.add_argument(
            "--name", type=str, required=True, help="Nazwa przestrzeni roboczej"
        )

        # Komenda: workspace unshare
        workspace_unshare_parser = workspace_subparsers.add_parser(
            "unshare", help="Wyłącza udostępnianie przestrzeni roboczej"
        )

        workspace_unshare_parser.add_argument(
            "--name", type=str, required=True, help="Nazwa przestrzeni roboczej"
        )

        # Komenda: api
        api_parser = subparsers.add_parser("api", help="Zarządzanie serwerem REST API")

        api_subparsers = api_parser.add_subparsers(
            dest="api_command", title="Komendy API", help="Komenda API do wykonania"
        )

        # Komenda: api start
        api_start_parser = api_subparsers.add_parser(
            "start", help="Uruchamia serwer REST API"
        )

        api_start_parser.add_argument(
            "--host",
            type=str,
            default="0.0.0.0",
            help="Adres hosta (domyślnie: 0.0.0.0)",
        )

        api_start_parser.add_argument(
            "--port", type=int, default=8000, help="Port (domyślnie: 8000)"
        )

        api_start_parser.add_argument(
            "--daemon", action="store_true", help="Uruchamia serwer w tle jako daemon"
        )

        api_start_parser.add_argument(
            "--log-file",
            type=str,
            help="Ścieżka do pliku logów (domyślnie: ~/.twinshare/logs/api.log)",
        )

        # Komenda: api stop
        api_stop_parser = api_subparsers.add_parser(
            "stop", help="Zatrzymuje serwer REST API uruchomiony w tle"
        )

        # Komenda: api status
        api_status_parser = api_subparsers.add_parser(
            "status", help="Sprawdza status serwera REST API"
        )

        return parser

    def _setup_logging(self, debug: bool = False) -> None:
        """
        Konfiguruje system logowania.

        Args:
            debug: Czy włączyć tryb debugowania
        """
        log_level = logging.DEBUG if debug else logging.INFO

        # Konfiguracja głównego loggera
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Ładuje konfigurację.

        Args:
            config_path: Ścieżka do pliku konfiguracyjnego
        """
        if config_path:
            config.load_from_file(config_path)

    def _format_output(self, data: Any, format_type: str = "table") -> str:
        """
        Formatuje dane wyjściowe.

        Args:
            data: Dane do sformatowania
            format_type: Typ formatu (table, json, yaml)

        Returns:
            str: Sformatowane dane
        """
        if format_type == "json":
            return json.dumps(data, indent=2)
        elif format_type == "yaml":
            import yaml

            return yaml.dump(data, default_flow_style=False)
        else:  # table
            from tabulate import tabulate

            if isinstance(data, list) and data and isinstance(data[0], dict):
                headers = data[0].keys()
                rows = [[item.get(h, "") for h in headers] for item in data]
                return tabulate(rows, headers=headers, tablefmt="grid")
            elif isinstance(data, dict):
                rows = [[k, v] for k, v in data.items()]
                return tabulate(rows, headers=["Klucz", "Wartość"], tablefmt="grid")
            else:
                return str(data)

    async def _handle_vm_command(self, args: argparse.Namespace) -> None:
        """
        Obsługuje komendy związane z maszynami wirtualnymi.

        Args:
            args: Argumenty wiersza poleceń
        """
        if args.vm_command == "list":
            vms = self.vm_runtime.list_vms()
            print(self._format_output(vms, args.format))

        elif args.vm_command == "create":
            try:
                result = self.vm_runtime.create_vm(
                    name=args.name,
                    image=args.image,
                    cpu_cores=args.cpu,
                    memory=args.memory,
                    disk_size=args.disk,
                    network=args.network,
                    hypervisor=args.hypervisor,
                )
                print(f"Utworzono maszynę wirtualną: {args.name}")
                print(self._format_output(result, "json"))
            except Exception as e:
                print(f"Błąd podczas tworzenia maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.vm_command == "start":
            try:
                self.vm_runtime.start_vm(args.name)
                print(f"Uruchomiono maszynę wirtualną: {args.name}")
            except Exception as e:
                print(f"Błąd podczas uruchamiania maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.vm_command == "stop":
            try:
                self.vm_runtime.stop_vm(args.name, force=args.force)
                print(f"Zatrzymano maszynę wirtualną: {args.name}")
            except Exception as e:
                print(f"Błąd podczas zatrzymywania maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.vm_command == "delete":
            try:
                self.vm_runtime.delete_vm(args.name, delete_disk=not args.keep_disk)
                print(f"Usunięto maszynę wirtualną: {args.name}")
            except Exception as e:
                print(f"Błąd podczas usuwania maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.vm_command == "status":
            try:
                status = self.vm_runtime.get_vm_status(args.name)
                print(self._format_output(status, "table"))
            except Exception as e:
                print(f"Błąd podczas pobierania statusu maszyny wirtualnej: {e}")
                sys.exit(1)

        else:
            print("Nieznana komenda VM")
            sys.exit(1)

    async def _handle_p2p_command(self, args: argparse.Namespace) -> None:
        """
        Obsługuje komendy związane z siecią P2P.

        Args:
            args: Argumenty wiersza poleceń
        """
        if args.p2p_command == "start":
            discovery.start()
            await network.start()
            print("Uruchomiono usługi P2P")

        elif args.p2p_command == "stop":
            await network.stop()
            discovery.stop()
            print("Zatrzymano usługi P2P")

        elif args.p2p_command == "list":
            peers = discovery.get_peers()
            print(self._format_output(peers, args.format))

        elif args.p2p_command == "send":
            try:
                # Parsuj dane JSON
                data = json.loads(args.data)

                # Utwórz wiadomość
                message = Message(
                    message_type=args.message_type,
                    data=data,
                    sender_id=discovery.peer_id,
                    receiver_id=args.peer_id,
                )

                # Wyślij wiadomość
                response = await network.send_message(
                    peer_id=args.peer_id, message_type=args.message_type, data=data
                )

                print("Wysłano wiadomość:")
                print(self._format_output(message.to_dict(), "json"))

                if response:
                    print("\nOtrzymano odpowiedź:")
                    print(self._format_output(response, "json"))

            except Exception as e:
                print(f"Błąd podczas wysyłania wiadomości: {e}")
                sys.exit(1)

        elif args.p2p_command == "status":
            print("Status usług P2P:")
            print(
                f"  Discovery: {'Uruchomiony' if discovery.is_running() else 'Zatrzymany'}"
            )
            print(
                f"  Network: {'Uruchomiony' if network.is_running() else 'Zatrzymany'}"
            )

        else:
            print("Nieznana komenda P2P")
            sys.exit(1)

    async def _handle_remote_command(self, args: argparse.Namespace) -> None:
        """
        Obsługuje komendy związane ze zdalnym zarządzaniem.

        Args:
            args: Argumenty wiersza poleceń
        """
        if args.remote_command == "vm-list":
            try:
                # Utwórz wiadomość
                message = VMListMessage(
                    sender_id=discovery.peer_id, receiver_id=args.peer
                )

                # Wyślij wiadomość
                response = await network.send_message(
                    peer_id=args.peer, message_type=message.type, data=message.data
                )

                if response:
                    print(self._format_output(response.get("vms", []), args.format))
                else:
                    print("Brak odpowiedzi od węzła")
                    sys.exit(1)

            except Exception as e:
                print(f"Błąd podczas listowania zdalnych maszyn wirtualnych: {e}")
                sys.exit(1)

        elif args.remote_command == "vm-create":
            try:
                # Utwórz wiadomość
                message = VMCreateMessage(
                    name=args.name,
                    image=args.image,
                    cpu_cores=args.cpu,
                    memory=args.memory,
                    disk_size=args.disk,
                    sender_id=discovery.peer_id,
                    receiver_id=args.peer,
                )

                # Wyślij wiadomość
                response = await network.send_message(
                    peer_id=args.peer, message_type=message.type, data=message.data
                )

                if response:
                    if response.get("status") == 200:
                        print(f"Utworzono zdalną maszynę wirtualną: {args.name}")
                        print(self._format_output(response, "json"))
                    else:
                        print(f"Błąd: {response.get('error', 'Nieznany błąd')}")
                        sys.exit(1)
                else:
                    print("Brak odpowiedzi od węzła")
                    sys.exit(1)

            except Exception as e:
                print(f"Błąd podczas tworzenia zdalnej maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.remote_command == "vm-start":
            try:
                # Utwórz wiadomość
                message = VMStartMessage(
                    vm_id=args.vm_id,
                    sender_id=discovery.peer_id,
                    receiver_id=args.peer,
                )

                # Wyślij wiadomość
                response = await network.send_message(
                    peer_id=args.peer, message_type=message.type, data=message.data
                )

                if response:
                    if response.get("status") == 200:
                        print(f"Uruchomiono zdalną maszynę wirtualną: {args.vm_id}")
                    else:
                        print(f"Błąd: {response.get('error', 'Nieznany błąd')}")
                        sys.exit(1)
                else:
                    print("Brak odpowiedzi od węzła")
                    sys.exit(1)

            except Exception as e:
                print(f"Błąd podczas uruchamiania zdalnej maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.remote_command == "vm-stop":
            try:
                # Utwórz wiadomość
                message = VMStopMessage(
                    vm_id=args.vm_id,
                    force=args.force,
                    sender_id=discovery.peer_id,
                    receiver_id=args.peer,
                )

                # Wyślij wiadomość
                response = await network.send_message(
                    peer_id=args.peer, message_type=message.type, data=message.data
                )

                if response:
                    if response.get("status") == 200:
                        print(f"Zatrzymano zdalną maszynę wirtualną: {args.vm_id}")
                    else:
                        print(f"Błąd: {response.get('error', 'Nieznany błąd')}")
                        sys.exit(1)
                else:
                    print("Brak odpowiedzi od węzła")
                    sys.exit(1)

            except Exception as e:
                print(f"Błąd podczas zatrzymywania zdalnej maszyny wirtualnej: {e}")
                sys.exit(1)

        elif args.remote_command == "vm-delete":
            try:
                # Utwórz wiadomość
                message = VMDeleteMessage(
                    vm_id=args.vm_id,
                    delete_disk=not args.keep_disk,
                    sender_id=discovery.peer_id,
                    receiver_id=args.peer,
                )

                # Wyślij wiadomość
                response = await network.send_message(
                    peer_id=args.peer, message_type=message.type, data=message.data
                )

                if response:
                    if response.get("status") == 200:
                        print(f"Usunięto zdalną maszynę wirtualną: {args.vm_id}")
                    else:
                        print(f"Błąd: {response.get('error', 'Nieznany błąd')}")
                        sys.exit(1)
                else:
                    print("Brak odpowiedzi od węzła")
                    sys.exit(1)

            except Exception as e:
                print(f"Błąd podczas usuwania zdalnej maszyny wirtualnej: {e}")
                sys.exit(1)

        else:
            print("Nieznana komenda zdalna")
            sys.exit(1)

    async def _handle_workspace_command(self, args: argparse.Namespace) -> None:
        """
        Obsługuje komendy związane z przestrzeniami roboczymi.

        Args:
            args: Argumenty wiersza poleceń
        """
        if args.workspace_command == "list":
            # Implementacja listowania przestrzeni roboczych
            # Na razie zwracamy pustą listę
            workspaces = []
            print(self._format_output(workspaces, args.format))
        elif args.workspace_command == "share":
            # Implementacja udostępniania przestrzeni roboczej
            workspace_name = args.name

            # Wywołanie API do udostępnienia workspace'a
            try:
                # W rzeczywistej implementacji, wywołaj odpowiednie API
                # Na razie tylko logujemy akcję
                logger.info(f"Udostępniono workspace '{workspace_name}'")
                print(f"Workspace '{workspace_name}' został udostępniony")
            except Exception as e:
                logger.error(f"Błąd podczas udostępniania workspace'a: {e}")
                print(f"Błąd: {e}")
        elif args.workspace_command == "unshare":
            # Implementacja wyłączania udostępniania przestrzeni roboczej
            workspace_name = args.name

            # Wywołanie API do wyłączenia udostępnienia workspace'a
            try:
                # W rzeczywistej implementacji, wywołaj odpowiednie API
                # Na razie tylko logujemy akcję
                logger.info(f"Wyłączono udostępnianie workspace'a '{workspace_name}'")
                print(f"Wyłączono udostępnianie workspace'a '{workspace_name}'")
            except Exception as e:
                logger.error(f"Błąd podczas wyłączania udostępniania workspace'a: {e}")
                print(f"Błąd: {e}")
        else:
            print("Nieznana komenda workspace")

    async def _handle_api_command(self, args: argparse.Namespace) -> None:
        """
        Obsługuje komendy związane z serwerem REST API.

        Args:
            args: Argumenty wiersza poleceń
        """
        if args.api_command == "start":
            try:
                # Określ domyślną ścieżkę do pliku logów, jeśli nie podano
                log_file = args.log_file
                if not log_file:
                    home_dir = os.path.expanduser("~")
                    log_dir = os.path.join(home_dir, ".twinshare", "logs")
                    os.makedirs(log_dir, exist_ok=True)
                    log_file = os.path.join(log_dir, "api.log")

                # Określ ścieżkę do pliku PID
                pid_dir = os.path.join(os.path.expanduser("~"), ".twinshare", "run")
                os.makedirs(pid_dir, exist_ok=True)
                pid_file = os.path.join(pid_dir, "api.pid")

                if args.daemon:
                    # Uruchom serwer w tle
                    print(
                        f"Uruchamianie serwera REST API w tle na {args.host}:{args.port}"
                    )
                    print(f"Logi będą zapisywane do: {log_file}")
                    print(f"PID będzie zapisany do: {pid_file}")

                    # Uruchom skrypt start_rest_api.py jako proces w tle
                    script_path = os.path.join(
                        parent_dir, "scripts", "start_rest_api.py"
                    )
                    cmd = [
                        sys.executable,
                        script_path,
                        "start",
                        "--host",
                        args.host,
                        "--port",
                        str(args.port),
                        "--log-file",
                        log_file,
                        "--pid-file",
                        pid_file,
                    ]

                    # Uruchom proces w tle
                    import subprocess

                    subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )

                    # Poczekaj chwilę, aby proces mógł się uruchomić
                    time.sleep(1)

                    # Sprawdź, czy proces się uruchomił
                    if os.path.exists(pid_file):
                        with open(pid_file, "r") as f:
                            pid = int(f.read().strip())
                        print(f"Serwer REST API został uruchomiony (PID: {pid})")
                    else:
                        print("Nie udało się uruchomić serwera REST API")
                else:
                    # Uruchom serwer w trybie interaktywnym
                    print(f"Uruchamianie serwera REST API na {args.host}:{args.port}")
                    print("Naciśnij Ctrl+C, aby zatrzymać serwer")

                    # Skonfiguruj logowanie
                    logging.basicConfig(
                        level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                    )

                    # Uruchom serwer
                    server = await start_server(args.host, args.port)

                    # Czekaj na przerwanie
                    try:
                        # Utrzymuj serwer uruchomiony
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        # Zatrzymaj serwer
                        await server.stop()
                        print("\nSerwer REST API został zatrzymany")
            except Exception as e:
                logger.error(f"Błąd podczas uruchamiania serwera REST API: {e}")
                print(f"Błąd: {e}")

        elif args.api_command == "stop":
            try:
                # Określ ścieżkę do pliku PID
                pid_dir = os.path.join(os.path.expanduser("~"), ".twinshare", "run")
                pid_file = os.path.join(pid_dir, "api.pid")

                # Sprawdź, czy plik PID istnieje
                if not os.path.exists(pid_file):
                    print("Serwer REST API nie jest uruchomiony")
                    return

                # Odczytaj PID z pliku
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())

                # Sprawdź, czy proces istnieje
                try:
                    os.kill(pid, 0)  # Sprawdza, czy proces istnieje
                except OSError:
                    print("Serwer REST API nie jest uruchomiony")
                    os.remove(pid_file)
                    return

                # Wyślij sygnał SIGTERM do procesu
                print(f"Zatrzymywanie serwera REST API (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)

                # Poczekaj chwilę, aby proces mógł się zatrzymać
                time.sleep(1)

                # Sprawdź, czy proces nadal istnieje
                try:
                    os.kill(pid, 0)
                    print("Serwer REST API nie odpowiada, wymuszam zatrzymanie...")
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

                # Usuń plik PID
                if os.path.exists(pid_file):
                    os.remove(pid_file)

                print("Serwer REST API został zatrzymany")
            except Exception as e:
                logger.error(f"Błąd podczas zatrzymywania serwera REST API: {e}")
                print(f"Błąd: {e}")

        elif args.api_command == "status":
            try:
                # Określ ścieżkę do pliku PID
                pid_dir = os.path.join(os.path.expanduser("~"), ".twinshare", "run")
                pid_file = os.path.join(pid_dir, "api.pid")

                # Sprawdź, czy plik PID istnieje
                if not os.path.exists(pid_file):
                    print("Status serwera REST API: Zatrzymany")
                    return

                # Odczytaj PID z pliku
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())

                # Sprawdź, czy proces istnieje
                try:
                    os.kill(pid, 0)  # Sprawdza, czy proces istnieje
                    print(f"Status serwera REST API: Uruchomiony (PID: {pid})")
                except OSError:
                    print(
                        "Status serwera REST API: Zatrzymany (plik PID istnieje, ale proces nie działa)"
                    )
                    os.remove(pid_file)
            except Exception as e:
                logger.error(f"Błąd podczas pobierania statusu serwera REST API: {e}")
                print(f"Błąd: {e}")
            sys.exit(1)

    async def run(self, args: Optional[List[str]] = None) -> None:
        """
        Uruchamia interfejs wiersza poleceń.

        Args:
            args: Argumenty wiersza poleceń
        """
        # Parsuj argumenty
        parsed_args = self.parser.parse_args(args)

        # Konfiguruj logowanie
        self._setup_logging(parsed_args.debug)

        # Ładuj konfigurację
        self._load_config(parsed_args.config)

        # Obsłuż komendy
        if parsed_args.command == "vm":
            await self._handle_vm_command(parsed_args)
        elif parsed_args.command == "p2p":
            await self._handle_p2p_command(parsed_args)
        elif parsed_args.command == "remote":
            await self._handle_remote_command(parsed_args)
        elif parsed_args.command == "workspace":
            await self._handle_workspace_command(parsed_args)
        elif parsed_args.command == "api":
            await self._handle_api_command(parsed_args)
        else:
            self.parser.print_help()


def main() -> None:
    """Funkcja główna CLI"""
    try:
        cli = CLI()
        asyncio.run(cli.run())
    except ImportError as e:
        print(f"Błąd importu: {e}")
        print("Sprawdź czy wszystkie zależności są zainstalowane.")
        sys.exit(1)
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
