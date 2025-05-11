#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł API dla zarządzania siecią P2P.

Zapewnia interfejs API do zarządzania siecią P2P,
umożliwiając integrację z innymi aplikacjami.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from ..p2p.discovery import discovery
from ..p2p.network import network
from ..p2p.protocol import Message

logger = logging.getLogger("ai-env-manager.api.p2p")


class P2PAPI:
    """
    Klasa implementująca API do zarządzania siecią P2P.

    Zapewnia metody do zarządzania siecią P2P, w tym uruchamianie i zatrzymywanie
    usług P2P, listowanie węzłów oraz wysyłanie wiadomości.
    """

    def __init__(self):
        """Inicjalizuje API sieci P2P"""
        pass

    async def start_services(self) -> bool:
        """
        Uruchamia usługi P2P.

        Returns:
            bool: Czy operacja się powiodła
        """
        try:
            discovery.start()
            await network.start()
            return True
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania usług P2P: {e}")
            return False

    async def stop_services(self) -> bool:
        """
        Zatrzymuje usługi P2P.

        Returns:
            bool: Czy operacja się powiodła
        """
        try:
            await network.stop()
            discovery.stop()
            return True
        except Exception as e:
            logger.error(f"Błąd podczas zatrzymywania usług P2P: {e}")
            return False

    def get_peers(self) -> List[Dict[str, Any]]:
        """
        Pobiera listę węzłów w sieci P2P.

        Returns:
            List[Dict[str, Any]]: Lista węzłów
        """
        return discovery.get_peers()

    def get_peer_info(self, peer_id: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera informacje o węźle.

        Args:
            peer_id: Identyfikator węzła

        Returns:
            Optional[Dict[str, Any]]: Informacje o węźle lub None, jeśli węzeł nie istnieje
        """
        peers = discovery.get_peers()
        for peer in peers:
            if peer.get("id") == peer_id:
                return peer
        return None

    def get_local_peer_id(self) -> str:
        """
        Pobiera identyfikator lokalnego węzła.

        Returns:
            str: Identyfikator lokalnego węzła
        """
        return discovery.peer_id

    def get_local_peer_info(self) -> Dict[str, Any]:
        """
        Pobiera informacje o lokalnym węźle.

        Returns:
            Dict[str, Any]: Informacje o lokalnym węźle
        """
        return {
            "id": discovery.peer_id,
            "name": discovery.peer_name,
            "address": discovery.peer_address,
            "port": discovery.peer_port,
            "services": discovery.services,
        }

    async def send_message(
        self, peer_id: str, message_type: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Wysyła wiadomość do węzła.

        Args:
            peer_id: Identyfikator węzła docelowego
            message_type: Typ wiadomości
            data: Dane wiadomości

        Returns:
            Optional[Dict[str, Any]]: Odpowiedź z węzła docelowego lub None, jeśli nie otrzymano odpowiedzi
        """
        try:
            response = await network.send_message(
                peer_id=peer_id, message_type=message_type, data=data
            )
            return response
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania wiadomości: {e}")
            return None

    async def broadcast_message(
        self, message_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Wysyła wiadomość do wszystkich węzłów.

        Args:
            message_type: Typ wiadomości
            data: Dane wiadomości

        Returns:
            Dict[str, Any]: Słownik odpowiedzi z węzłów docelowych (peer_id -> odpowiedź)
        """
        responses = {}
        peers = discovery.get_peers()

        for peer in peers:
            peer_id = peer.get("id")
            try:
                response = await network.send_message(
                    peer_id=peer_id, message_type=message_type, data=data
                )
                responses[peer_id] = response
            except Exception as e:
                logger.error(f"Błąd podczas wysyłania wiadomości do {peer_id}: {e}")
                responses[peer_id] = {"error": str(e)}

        return responses

    async def send_file(
        self, peer_id: str, file_path: str, remote_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Wysyła plik do węzła.

        Args:
            peer_id: Identyfikator węzła docelowego
            file_path: Ścieżka do pliku
            remote_path: Ścieżka docelowa na węźle docelowym

        Returns:
            Optional[Dict[str, Any]]: Odpowiedź z węzła docelowego lub None, jeśli nie otrzymano odpowiedzi
        """
        try:
            response = await network.send_file(
                peer_id=peer_id, file_path=file_path, remote_path=remote_path
            )
            return response
        except Exception as e:
            logger.error(f"Błąd podczas wysyłania pliku: {e}")
            return None

    async def request_file(
        self, peer_id: str, remote_path: str, local_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Pobiera plik z węzła.

        Args:
            peer_id: Identyfikator węzła docelowego
            remote_path: Ścieżka do pliku na węźle docelowym
            local_path: Ścieżka docelowa na lokalnym węźle

        Returns:
            Optional[Dict[str, Any]]: Odpowiedź z węzła docelowego lub None, jeśli nie otrzymano odpowiedzi
        """
        try:
            response = await network.request_file(
                peer_id=peer_id, remote_path=remote_path, local_path=local_path
            )
            return response
        except Exception as e:
            logger.error(f"Błąd podczas pobierania pliku: {e}")
            return None
