# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł wykrywania peer-to-peer dla AI Environment Manager.

Implementuje automatyczne wykrywanie węzłów w sieci lokalnej
i utrzymywanie informacji o dostępnych środowiskach.
"""

import json
import logging
import os
import socket
import threading
import time
import uuid
import zlib
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from ..core.config import Config, config

logger = logging.getLogger("ai-env-manager.p2p.discovery")


class PeerInfo:
    """Informacje o węźle w sieci P2P"""

    def __init__(self, peer_id: str, hostname: str, ip: str, timestamp: str):
        self.peer_id = peer_id
        self.hostname = hostname
        self.ip = ip
        self.timestamp = timestamp
        self.last_seen = datetime.now().isoformat()
        self.environments = []
        self.status = "active"
        self.version = ""
        self.features = []

    def update(self, data: Dict[str, Any]) -> None:
        """Aktualizuje informacje o węźle"""
        self.hostname = data.get("hostname", self.hostname)
        self.ip = data.get("ip", self.ip)
        self.timestamp = data.get("timestamp", self.timestamp)
        self.last_seen = datetime.now().isoformat()
        self.environments = data.get("environments", self.environments)
        self.version = data.get("version", self.version)
        self.features = data.get("features", self.features)

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje informacje o węźle do słownika"""
        return {
            "peer_id": self.peer_id,
            "hostname": self.hostname,
            "ip": self.ip,
            "timestamp": self.timestamp,
            "last_seen": self.last_seen,
            "environments": self.environments,
            "status": self.status,
            "version": self.version,
            "features": self.features,
        }


class P2PDiscovery:
    """Implementacja wykrywania peer-to-peer"""

    def __init__(self):
        self.running = False
        self.listen_thread = None
        self.broadcast_thread = None
        self.peers = {}  # peer_id -> PeerInfo
        self.callbacks = []
        self.port = config.get("p2p.discovery.port", 37777)
        self.broadcast_interval = config.get("p2p.discovery.broadcast_interval", 10)
        self.peer_timeout = config.get("p2p.discovery.peer_timeout", 60)

        # Generuj ID węzła jeśli nie istnieje
        self.peer_id = config.get("p2p.node.id")
        if not self.peer_id:
            self.peer_id = str(uuid.uuid4())
            config.set("p2p.node.id", self.peer_id)

        # Informacje o bieżącym węźle
        self.node_info = {
            "peer_id": self.peer_id,
            "hostname": config.get("p2p.node.hostname", socket.gethostname()),
            "ip": self._get_local_ip(),
            "timestamp": datetime.now().isoformat(),
            "version": config.get("version", "1.0.0"),
            "environments": [],
            "features": self._get_supported_features(),
        }

    def start(self) -> bool:
        """Uruchamia wykrywanie P2P"""
        if self.running:
            logger.info("Wykrywanie P2P już działa")
            return False

        self.running = True

        # Uruchom wątek nasłuchujący
        self.listen_thread = threading.Thread(target=self._listen_for_peers)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        # Uruchom wątek rozgłaszający
        self.broadcast_thread = threading.Thread(target=self._broadcast_presence)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()

        logger.info(f"Uruchomiono wykrywanie P2P na porcie {self.port}")
        return True

    def stop(self) -> bool:
        """Zatrzymuje wykrywanie P2P"""
        if not self.running:
            logger.info("Wykrywanie P2P już jest zatrzymane")
            return False

        self.running = False

        # Poczekaj na zakończenie wątków
        if self.listen_thread:
            self.listen_thread.join(1)

        if self.broadcast_thread:
            self.broadcast_thread.join(1)

        logger.info("Zatrzymano wykrywanie P2P")
        return True

    def register_callback(self, callback: Callable[[str, PeerInfo], None]) -> None:
        """Rejestruje funkcję zwrotną wywoływaną przy wykryciu/aktualizacji węzła"""
        self.callbacks.append(callback)

    def get_peers(self) -> List[Dict[str, Any]]:
        """Zwraca listę aktywnych węzłów"""
        self._cleanup_peers()
        return [
            peer.to_dict() for peer in self.peers.values() if peer.status == "active"
        ]

    def get_peer(self, peer_id: str) -> Optional[Dict[str, Any]]:
        """Zwraca informacje o konkretnym węźle"""
        if peer_id in self.peers:
            return self.peers[peer_id].to_dict()
        return None

    def update_environments(self, environments: List[Dict[str, Any]]) -> None:
        """Aktualizuje listę udostępnionych środowisk"""
        self.node_info["environments"] = environments
        self.node_info["timestamp"] = datetime.now().isoformat()

    def _get_local_ip(self) -> str:
        """Pobiera lokalny adres IP"""
        try:
            # Utwórz gniazdo, które łączy się z zewnętrznym serwerem
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            # Pobierz adres IP za pomocą hostname
            return socket.gethostbyname(socket.gethostname())

    def _get_supported_features(self) -> List[str]:
        """Zwraca listę obsługiwanych funkcji"""
        features = []

        # Sprawdź dostępność wirtualizacji
        if config.get("runtime.vm.enabled", False):
            features.append("vm")

        # Sprawdź dostępność kontenerów
        if config.get("runtime.container.enabled", False):
            features.append("container")

        # Sprawdź dostępność procesów lokalnych
        if config.get("runtime.process.enabled", False):
            features.append("process")

        # Sprawdź dostępność federacji
        if config.get("p2p.federation.enabled", False):
            features.append("federation")

        return features

    def _listen_for_peers(self) -> None:
        """Nasłuchuje rozgłoszeń od innych węzłów"""
        try:
            # Utwórz gniazdo UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", self.port))
            sock.settimeout(1)

            logger.info(f"Nasłuchiwanie węzłów P2P na porcie {self.port}")

            while self.running:
                try:
                    # Odbierz dane
                    data, addr = sock.recvfrom(4096)

                    # Dekompresuj i zdekoduj dane
                    try:
                        decompressed_data = zlib.decompress(data)
                        peer_data = json.loads(decompressed_data.decode("utf-8"))

                        # Dodaj adres IP nadawcy
                        peer_data["ip"] = addr[0]

                        # Pobierz ID węzła
                        peer_id = peer_data.get("peer_id")

                        # Ignoruj własne rozgłoszenia
                        if peer_id == self.peer_id:
                            continue

                        # Przetwórz informacje o węźle
                        if peer_id:
                            # Sprawdź czy to nowy węzeł
                            is_new = peer_id not in self.peers

                            if is_new:
                                # Nowy węzeł
                                peer_info = PeerInfo(
                                    peer_id=peer_id,
                                    hostname=peer_data.get("hostname", "Unknown"),
                                    ip=peer_data.get("ip", addr[0]),
                                    timestamp=peer_data.get(
                                        "timestamp", datetime.now().isoformat()
                                    ),
                                )
                                peer_info.update(peer_data)
                                self.peers[peer_id] = peer_info

                                logger.info(
                                    f"Odkryto nowy węzeł: {peer_info.hostname} ({peer_info.ip})"
                                )
                            else:
                                # Zaktualizuj istniejący węzeł
                                self.peers[peer_id].update(peer_data)
                                logger.debug(
                                    f"Zaktualizowano węzeł: {self.peers[peer_id].hostname} ({self.peers[peer_id].ip})"
                                )

                            # Wywołaj funkcje zwrotne
                            for callback in self.callbacks:
                                try:
                                    callback(peer_id, self.peers[peer_id])
                                except Exception as e:
                                    logger.error(
                                        f"Błąd podczas wywoływania funkcji zwrotnej: {e}"
                                    )

                    except Exception as e:
                        logger.error(f"Błąd podczas przetwarzania rozgłoszenia: {e}")

                except socket.timeout:
                    pass
                except Exception as e:
                    logger.error(f"Błąd podczas nasłuchiwania: {e}")
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia gniazda nasłuchującego: {e}")
        finally:
            sock.close()
            logger.info("Zatrzymano nasłuchiwanie węzłów P2P")

    def _broadcast_presence(self) -> None:
        """Rozgłasza obecność węzła w sieci"""
        try:
            # Utwórz gniazdo UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            logger.info(
                f"Rozpoczęto rozgłaszanie obecności węzła w sieci na porcie {self.port}"
            )

            while self.running:
                try:
                    # Aktualizuj informacje o węźle
                    self.node_info["ip"] = self._get_local_ip()
                    self.node_info["timestamp"] = datetime.now().isoformat()

                    # Serializuj, skompresuj i wyślij dane
                    json_data = json.dumps(self.node_info).encode("utf-8")
                    compressed_data = zlib.compress(json_data)

                    # Wyślij do adresu broadcast
                    sock.sendto(compressed_data, ("<broadcast>", self.port))

                    logger.debug(
                        f"Rozgłoszono obecność węzła: {self.node_info['hostname']} ({self.node_info['ip']})"
                    )

                    # Poczekaj przed następnym rozgłoszeniem
                    time.sleep(self.broadcast_interval)
                except Exception as e:
                    logger.error(f"Błąd podczas rozgłaszania: {e}")
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia gniazda rozgłaszającego: {e}")
        finally:
            sock.close()
            logger.info("Zatrzymano rozgłaszanie obecności węzła")

    def _cleanup_peers(self) -> None:
        """Usuwa nieaktywne węzły"""
        now = datetime.now()
        peers_to_update = []

        for peer_id, peer in self.peers.items():
            try:
                last_seen = datetime.fromisoformat(peer.last_seen)
                elapsed = (now - last_seen).total_seconds()

                if elapsed > self.peer_timeout:
                    # Oznacz węzeł jako nieaktywny
                    if peer.status == "active":
                        peer.status = "inactive"
                        peers_to_update.append(peer_id)
                        logger.info(
                            f"Węzeł {peer.hostname} ({peer.ip}) oznaczony jako nieaktywny"
                        )
            except Exception as e:
                logger.error(f"Błąd podczas czyszczenia węzłów: {e}")

        # Wywołaj funkcje zwrotne dla zaktualizowanych węzłów
        for peer_id in peers_to_update:
            for callback in self.callbacks:
                try:
                    callback(peer_id, self.peers[peer_id])
                except Exception as e:
                    logger.error(f"Błąd podczas wywoływania funkcji zwrotnej: {e}")


# Inicjalizuj moduł
discovery = P2PDiscovery()
