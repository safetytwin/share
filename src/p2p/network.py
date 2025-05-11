#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł sieci P2P dla AI Environment Manager.

Implementuje komunikację między węzłami w sieci P2P,
umożliwiając wymianę danych, zdalne wywołania i transfer plików.
"""

import asyncio
import hashlib
import json
import logging
import os
import socket
import ssl
import threading
import time
import uuid
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import aiohttp
from aiohttp import web

from ..core.config import config
from .discovery import PeerInfo, discovery

logger = logging.getLogger("ai-env-manager.p2p.network")


class P2PNetwork:
    """
    Klasa implementująca komunikację sieciową P2P.

    Umożliwia wymianę danych między węzłami, zdalne wywołania
    funkcji i transfer plików po wykryciu węzłów przez moduł discovery.
    """

    def __init__(self):
        """Inicjalizuje sieć P2P"""
        self.running = False
        self.server = None
        self.server_task = None
        self.port = config.get("p2p.network.port", 37778)
        self.use_ssl = config.get("p2p.network.ssl", True)
        self.max_message_size = config.get(
            "p2p.network.max_message_size", 10 * 1024 * 1024
        )  # 10 MB
        self.timeout = config.get("p2p.network.timeout", 30)  # 30 sekund

        # Słownik zarejestrowanych handlerów
        self.handlers = {}

        # Informacje o węzłach z modułu discovery
        self.discovery = discovery

        # Klucze i certyfikaty SSL
        self.ssl_context = None
        if self.use_ssl:
            self._setup_ssl()

        # Zarejestruj podstawowe handlery
        self._register_default_handlers()

    def _setup_ssl(self) -> None:
        """Konfiguruje kontekst SSL dla bezpiecznej komunikacji"""
        try:
            cert_dir = Path(
                config.get("paths.certificates", config.CONFIG_DIR / "certificates")
            )
            cert_dir.mkdir(parents=True, exist_ok=True)

            cert_file = cert_dir / "server.crt"
            key_file = cert_dir / "server.key"

            # Jeśli certyfikaty nie istnieją, wygeneruj je
            if not cert_file.exists() or not key_file.exists():
                self._generate_self_signed_cert(cert_file, key_file)

            # Utwórz kontekst SSL
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(cert_file, key_file)

            logger.info("Skonfigurowano SSL dla komunikacji P2P")
        except Exception as e:
            logger.error(f"Błąd podczas konfiguracji SSL: {e}")
            self.use_ssl = False

    def _generate_self_signed_cert(self, cert_file: Path, key_file: Path) -> None:
        """Generuje samopodpisany certyfikat SSL"""
        try:
            import datetime

            from cryptography import x509
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.x509.oid import NameOID

            # Wygeneruj klucz prywatny
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

            # Zapisz klucz prywatny
            with open(key_file, "wb") as f:
                f.write(
                    private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )

            # Utwórz certyfikat
            subject = issuer = x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "PL"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Mazowieckie"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "Warszawa"),
                    x509.NameAttribute(
                        NameOID.ORGANIZATION_NAME, "AI Environment Manager"
                    ),
                    x509.NameAttribute(NameOID.COMMON_NAME, socket.gethostname()),
                ]
            )

            cert = (
                x509.CertificateBuilder()
                .subject_name(subject)
                .issuer_name(issuer)
                .public_key(private_key.public_key())
                .serial_number(x509.random_serial_number())
                .not_valid_before(datetime.datetime.utcnow())
                .not_valid_after(
                    datetime.datetime.utcnow() + datetime.timedelta(days=365)
                )
                .add_extension(
                    x509.SubjectAlternativeName([x509.DNSName(socket.gethostname())]),
                    critical=False,
                )
                .sign(private_key, hashes.SHA256())
            )

            # Zapisz certyfikat
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            logger.info(f"Wygenerowano samopodpisany certyfikat SSL: {cert_file}")
        except Exception as e:
            logger.error(f"Błąd podczas generowania certyfikatu SSL: {e}")
            raise

    def _register_default_handlers(self) -> None:
        """Rejestruje domyślne handlery wiadomości"""
        self.register_handler("ping", self._handle_ping)
        self.register_handler("get_info", self._handle_get_info)
        self.register_handler("get_environments", self._handle_get_environments)

    async def _handle_ping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obsługuje żądanie ping"""
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "node_id": self.discovery.peer_id,
        }

    async def _handle_get_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obsługuje żądanie informacji o węźle"""
        return {"status": "ok", "info": self.discovery.node_info}

    async def _handle_get_environments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Obsługuje żądanie listy środowisk"""
        return {
            "status": "ok",
            "environments": self.discovery.node_info.get("environments", []),
        }

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """
        Rejestruje handler dla określonego typu wiadomości.

        Args:
            message_type: Typ wiadomości
            handler: Funkcja obsługująca wiadomość
        """
        self.handlers[message_type] = handler
        logger.debug(f"Zarejestrowano handler dla wiadomości typu '{message_type}'")

    async def start_server(self) -> None:
        """Uruchamia serwer P2P"""
        app = web.Application()
        app.add_routes(
            [
                web.post("/message", self._handle_message),
                web.post("/file/upload", self._handle_file_upload),
                web.get("/file/download/{file_id}", self._handle_file_download),
            ]
        )

        # Konfiguracja serwera
        if self.use_ssl and self.ssl_context:
            self.server = await asyncio.get_event_loop().create_server(
                app.make_handler(), "0.0.0.0", self.port, ssl=self.ssl_context
            )
        else:
            self.server = await asyncio.get_event_loop().create_server(
                app.make_handler(), "0.0.0.0", self.port
            )

        logger.info(
            f"Uruchomiono serwer P2P na porcie {self.port} (SSL: {self.use_ssl})"
        )

    async def _handle_message(self, request: web.Request) -> web.Response:
        """Obsługuje przychodzące wiadomości"""
        try:
            # Sprawdź rozmiar wiadomości
            content_length = request.content_length
            if content_length and content_length > self.max_message_size:
                return web.json_response(
                    {
                        "status": "error",
                        "message": f"Message too large ({content_length} bytes)",
                    },
                    status=413,
                )

            # Odczytaj dane
            data = await request.json()

            # Sprawdź typ wiadomości
            message_type = data.get("type")
            if not message_type:
                return web.json_response(
                    {"status": "error", "message": "Missing message type"}, status=400
                )

            # Znajdź handler dla danego typu wiadomości
            handler = self.handlers.get(message_type)
            if not handler:
                return web.json_response(
                    {
                        "status": "error",
                        "message": f"Unknown message type: {message_type}",
                    },
                    status=400,
                )

            # Wywołaj handler
            result = await handler(data.get("data", {}))

            # Zwróć wynik
            return web.json_response(result)

        except Exception as e:
            logger.error(f"Błąd podczas obsługi wiadomości: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def _handle_file_upload(self, request: web.Request) -> web.Response:
        """Obsługuje przesyłanie plików"""
        try:
            # Sprawdź rozmiar pliku
            content_length = request.content_length
            if content_length and content_length > self.max_message_size:
                return web.json_response(
                    {
                        "status": "error",
                        "message": f"File too large ({content_length} bytes)",
                    },
                    status=413,
                )

            # Odczytaj dane multipart
            reader = await request.multipart()

            # Odczytaj metadane
            field = await reader.next()
            if field.name != "metadata":
                return web.json_response(
                    {"status": "error", "message": "Missing metadata field"}, status=400
                )

            metadata_json = await field.text()
            metadata = json.loads(metadata_json)

            # Odczytaj plik
            field = await reader.next()
            if field.name != "file":
                return web.json_response(
                    {"status": "error", "message": "Missing file field"}, status=400
                )

            # Generuj unikalny identyfikator pliku
            file_id = str(uuid.uuid4())

            # Utwórz katalog tymczasowy
            temp_dir = Path(config.get("paths.temp", config.CONFIG_DIR / "temp"))
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Zapisz plik
            file_path = temp_dir / file_id
            with open(file_path, "wb") as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)

            # Oblicz hash pliku
            file_hash = self._calculate_file_hash(file_path)

            # Zwróć identyfikator pliku
            return web.json_response(
                {"status": "ok", "file_id": file_id, "hash": file_hash}
            )

        except Exception as e:
            logger.error(f"Błąd podczas przesyłania pliku: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    async def _handle_file_download(self, request: web.Request) -> web.Response:
        """Obsługuje pobieranie plików"""
        try:
            # Pobierz identyfikator pliku
            file_id = request.match_info.get("file_id")
            if not file_id:
                return web.json_response(
                    {"status": "error", "message": "Missing file ID"}, status=400
                )

            # Sprawdź czy plik istnieje
            temp_dir = Path(config.get("paths.temp", config.CONFIG_DIR / "temp"))
            file_path = temp_dir / file_id

            if not file_path.exists():
                return web.json_response(
                    {"status": "error", "message": f"File not found: {file_id}"},
                    status=404,
                )

            # Zwróć plik
            return web.FileResponse(file_path)

        except Exception as e:
            logger.error(f"Błąd podczas pobierania pliku: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Oblicza hash pliku (SHA-256)"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def start(self) -> bool:
        """
        Uruchamia sieć P2P.

        Returns:
            bool: True jeśli uruchomienie się powiodło
        """
        if self.running:
            logger.info("Sieć P2P już działa")
            return False

        self.running = True

        # Uruchom serwer w tle
        self.server_task = asyncio.create_task(self.start_server())

        # Zarejestruj callback w module discovery
        self.discovery.register_callback(self._on_peer_discovered)

        logger.info("Uruchomiono sieć P2P")
        return True

    async def stop(self) -> bool:
        """
        Zatrzymuje sieć P2P.

        Returns:
            bool: True jeśli zatrzymanie się powiodło
        """
        if not self.running:
            logger.info("Sieć P2P już jest zatrzymana")
            return False

        self.running = False

        # Zatrzymaj serwer
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Anuluj zadanie serwera
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

        logger.info("Zatrzymano sieć P2P")
        return True

    def _on_peer_discovered(self, event: str, peer: PeerInfo) -> None:
        """
        Callback wywoływany przy wykryciu nowego węzła.

        Args:
            event: Typ zdarzenia (new, update, remove)
            peer: Informacje o węźle
        """
        if event == "new":
            logger.info(f"Wykryto nowy węzeł: {peer.hostname} ({peer.ip})")
            # Tutaj można dodać kod inicjujący komunikację z nowym węzłem
        elif event == "update":
            logger.debug(
                f"Zaktualizowano informacje o węźle: {peer.hostname} ({peer.ip})"
            )
        elif event == "remove":
            logger.info(f"Usunięto węzeł: {peer.hostname} ({peer.ip})")

    async def send_message(
        self, peer_id: str, message_type: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Wysyła wiadomość do określonego węzła.

        Args:
            peer_id: Identyfikator węzła docelowego
            message_type: Typ wiadomości
            data: Dane wiadomości

        Returns:
            Optional[Dict[str, Any]]: Odpowiedź lub None w przypadku błędu
        """
        # Obsługa specjalnych przypadków dla połączeń lokalnych
        local_identifiers = ["localhost", "127.0.0.1"]
        local_hostname = socket.gethostname()

        # Pobierz lokalne adresy IP
        local_ips = []
        try:
            for interface in socket.getaddrinfo(local_hostname, None):
                if interface[4][0] not in local_ips and not interface[4][0].startswith(
                    "127."
                ):
                    local_ips.append(interface[4][0])
        except:
            pass

        # Dodaj adres IP z konfiguracji
        local_ip = config.get("p2p.node.ip")
        if local_ip and local_ip not in local_ips:
            local_ips.append(local_ip)

        # Sprawdź, czy peer_id jest lokalnym identyfikatorem
        is_local = (
            peer_id in local_identifiers
            or peer_id == local_hostname
            or peer_id in local_ips
            or peer_id == self.discovery.peer_id
        )

        if is_local:
            # Użyj lokalnego handlera do obsługi wiadomości
            logger.info(f"Obsługa lokalnego żądania typu: {message_type}")

            # Znajdź odpowiedni handler
            handler = self.handlers.get(message_type)
            if not handler:
                logger.error(f"Nieznany typ wiadomości: {message_type}")
                return None

            # Wywołaj handler
            try:
                result = await handler(data)
                return result
            except Exception as e:
                logger.error(f"Błąd podczas obsługi lokalnej wiadomości: {e}")
                return None

        # Standardowa obsługa dla zdalnych węzłów
        # Pobierz informacje o węźle
        peer_info = self.discovery.get_peer(peer_id)
        if not peer_info:
            logger.error(f"Nie znaleziono węzła o ID: {peer_id}")
            return None

        # Przygotuj wiadomość
        message = {
            "type": message_type,
            "data": data,
            "sender": self.discovery.peer_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Wyślij wiadomość
        try:
            # Utwórz sesję HTTP
            async with aiohttp.ClientSession() as session:
                # Określ protokół (HTTP lub HTTPS)
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{peer_info['ip']}:{self.port}/message"

                # Wyślij żądanie POST
                async with session.post(
                    url,
                    json=message,
                    ssl=(
                        False if self.use_ssl else None
                    ),  # Ignoruj błędy SSL dla samopodpisanych certyfikatów
                    timeout=self.timeout,
                ) as response:
                    # Sprawdź status odpowiedzi
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Błąd podczas wysyłania wiadomości: {response.status} - {error_text}"
                        )
                        return None

                    # Zwróć odpowiedź
                    return await response.json()

        except Exception as e:
            logger.error(
                f"Błąd podczas wysyłania wiadomości do {peer_info['hostname']}: {e}"
            )
            return None

    async def upload_file(
        self, peer_id: str, file_path: Path, metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Przesyła plik do określonego węzła.

        Args:
            peer_id: Identyfikator węzła docelowego
            file_path: Ścieżka do pliku
            metadata: Metadane pliku

        Returns:
            Optional[Dict[str, Any]]: Informacje o przesłanym pliku lub None w przypadku błędu
        """
        # Pobierz informacje o węźle
        peer_info = self.discovery.get_peer(peer_id)
        if not peer_info:
            logger.error(f"Nie znaleziono węzła o ID: {peer_id}")
            return None

        # Sprawdź czy plik istnieje
        if not file_path.exists():
            logger.error(f"Plik nie istnieje: {file_path}")
            return None

        # Sprawdź rozmiar pliku
        file_size = file_path.stat().st_size
        if file_size > self.max_message_size:
            logger.error(f"Plik jest zbyt duży: {file_size} bajtów")
            return None

        # Wyślij plik
        try:
            # Utwórz sesję HTTP
            async with aiohttp.ClientSession() as session:
                # Określ protokół (HTTP lub HTTPS)
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{peer_info['ip']}:{self.port}/file/upload"

                # Przygotuj dane multipart
                data = aiohttp.FormData()
                data.add_field("metadata", json.dumps(metadata))
                data.add_field("file", open(file_path, "rb"), filename=file_path.name)

                # Wyślij żądanie POST
                async with session.post(
                    url,
                    data=data,
                    ssl=(
                        False if self.use_ssl else None
                    ),  # Ignoruj błędy SSL dla samopodpisanych certyfikatów
                    timeout=self.timeout,
                ) as response:
                    # Sprawdź status odpowiedzi
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Błąd podczas przesyłania pliku: {response.status} - {error_text}"
                        )
                        return None

                    # Zwróć odpowiedź
                    return await response.json()

        except Exception as e:
            logger.error(
                f"Błąd podczas przesyłania pliku do {peer_info['hostname']}: {e}"
            )
            return None

    async def download_file(
        self, peer_id: str, file_id: str, output_path: Path
    ) -> bool:
        """
        Pobiera plik z określonego węzła.

        Args:
            peer_id: Identyfikator węzła źródłowego
            file_id: Identyfikator pliku
            output_path: Ścieżka docelowa

        Returns:
            bool: True jeśli pobieranie się powiodło
        """
        # Pobierz informacje o węźle
        peer_info = self.discovery.get_peer(peer_id)
        if not peer_info:
            logger.error(f"Nie znaleziono węzła o ID: {peer_id}")
            return False

        # Pobierz plik
        try:
            # Utwórz sesję HTTP
            async with aiohttp.ClientSession() as session:
                # Określ protokół (HTTP lub HTTPS)
                protocol = "https" if self.use_ssl else "http"
                url = f"{protocol}://{peer_info['ip']}:{self.port}/file/download/{file_id}"

                # Wyślij żądanie GET
                async with session.get(
                    url,
                    ssl=(
                        False if self.use_ssl else None
                    ),  # Ignoruj błędy SSL dla samopodpisanych certyfikatów
                    timeout=self.timeout,
                ) as response:
                    # Sprawdź status odpowiedzi
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Błąd podczas pobierania pliku: {response.status} - {error_text}"
                        )
                        return False

                    # Zapisz plik
                    with open(output_path, "wb") as f:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)

                    logger.info(f"Pobrano plik {file_id} do {output_path}")
                    return True

        except Exception as e:
            logger.error(
                f"Błąd podczas pobierania pliku z {peer_info['hostname']}: {e}"
            )
            return False


# Inicjalizuj moduł
network = P2PNetwork()
