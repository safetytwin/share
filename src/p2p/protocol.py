#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Protokół komunikacyjny P2P dla AI Environment Manager.

Definiuje formaty wiadomości i protokoły komunikacyjne używane
do zarządzania maszynami wirtualnymi i innymi zasobami w sieci P2P.
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("ai-env-manager.p2p.protocol")


class MessageType(Enum):
    """Typy wiadomości protokołu P2P"""

    # Podstawowe typy wiadomości
    PING = "ping"
    PONG = "pong"
    ERROR = "error"

    # Wiadomości dotyczące węzłów
    NODE_INFO = "node_info"
    NODE_STATUS = "node_status"

    # Wiadomości dotyczące maszyn wirtualnych
    VM_LIST = "vm_list"
    VM_INFO = "vm_info"
    VM_CREATE = "vm_create"
    VM_START = "vm_start"
    VM_STOP = "vm_stop"
    VM_DELETE = "vm_delete"
    VM_STATUS = "vm_status"

    # Wiadomości dotyczące kontenerów
    CONTAINER_LIST = "container_list"
    CONTAINER_INFO = "container_info"
    CONTAINER_CREATE = "container_create"
    CONTAINER_START = "container_start"
    CONTAINER_STOP = "container_stop"
    CONTAINER_DELETE = "container_delete"
    CONTAINER_STATUS = "container_status"

    # Wiadomości dotyczące workspace'ów
    WORKSPACE_LIST = "workspace_list"
    WORKSPACE_INFO = "workspace_info"
    WORKSPACE_CREATE = "workspace_create"
    WORKSPACE_UPDATE = "workspace_update"
    WORKSPACE_DELETE = "workspace_delete"

    # Wiadomości dotyczące transferu plików
    FILE_TRANSFER_REQUEST = "file_transfer_request"
    FILE_TRANSFER_RESPONSE = "file_transfer_response"
    FILE_CHUNK = "file_chunk"
    FILE_TRANSFER_STATUS = "file_transfer_status"
    FILE_TRANSFER_COMPLETE = "file_transfer_complete"


class StatusCode(Enum):
    """Kody statusu odpowiedzi"""

    # Kody sukcesu (2xx)
    OK = 200
    CREATED = 201
    ACCEPTED = 202

    # Kody błędów klienta (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409

    # Kody błędów serwera (5xx)
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503


class Message:
    """
    Bazowa klasa wiadomości protokołu P2P.

    Definiuje podstawową strukturę wiadomości wymienianej
    między węzłami w sieci P2P.
    """

    def __init__(
        self,
        message_type: Union[MessageType, str],
        data: Dict[str, Any] = None,
        message_id: str = None,
        correlation_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość protokołu.

        Args:
            message_type: Typ wiadomości
            data: Dane wiadomości
            message_id: Unikalny identyfikator wiadomości
            correlation_id: Identyfikator korelacji (dla odpowiedzi)
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        # Konwertuj typ wiadomości na string jeśli to enum
        if isinstance(message_type, MessageType):
            self.type = message_type.value
        else:
            self.type = message_type

        # Inicjalizuj pozostałe pola
        self.data = data or {}
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje wiadomość do słownika"""
        result = {
            "type": self.type,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "data": self.data,
        }

        # Dodaj opcjonalne pola jeśli istnieją
        if self.correlation_id:
            result["correlation_id"] = self.correlation_id

        if self.sender_id:
            result["sender_id"] = self.sender_id

        if self.receiver_id:
            result["receiver_id"] = self.receiver_id

        return result

    def to_json(self) -> str:
        """Konwertuje wiadomość do formatu JSON"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """Tworzy wiadomość z słownika"""
        return cls(
            message_type=data.get("type"),
            data=data.get("data", {}),
            message_id=data.get("message_id"),
            correlation_id=data.get("correlation_id"),
            sender_id=data.get("sender_id"),
            receiver_id=data.get("receiver_id"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Tworzy wiadomość z JSON"""
        return cls.from_dict(json.loads(json_str))

    def create_response(
        self, data: Dict[str, Any] = None, status: StatusCode = StatusCode.OK
    ) -> "Message":
        """
        Tworzy wiadomość odpowiedzi na bieżącą wiadomość.

        Args:
            data: Dane odpowiedzi
            status: Kod statusu odpowiedzi

        Returns:
            Message: Nowa wiadomość odpowiedzi
        """
        response_data = data or {}
        response_data["status"] = (
            status.value if isinstance(status, StatusCode) else status
        )

        return Message(
            message_type=f"{self.type}_response",
            data=response_data,
            correlation_id=self.message_id,
            sender_id=self.receiver_id,
            receiver_id=self.sender_id,
        )

    def create_error_response(
        self, error_message: str, error_code: StatusCode = StatusCode.INTERNAL_ERROR
    ) -> "Message":
        """
        Tworzy wiadomość błędu w odpowiedzi na bieżącą wiadomość.

        Args:
            error_message: Komunikat błędu
            error_code: Kod błędu

        Returns:
            Message: Nowa wiadomość błędu
        """
        error_data = {
            "status": (
                error_code.value if isinstance(error_code, StatusCode) else error_code
            ),
            "error": error_message,
        }

        return Message(
            message_type=MessageType.ERROR.value,
            data=error_data,
            correlation_id=self.message_id,
            sender_id=self.receiver_id,
            receiver_id=self.sender_id,
        )


# Klasy wiadomości specyficzne dla VM


class VMListMessage(Message):
    """Wiadomość żądania listy maszyn wirtualnych"""

    def __init__(
        self,
        filters: Dict[str, Any] = None,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania listy VM.

        Args:
            filters: Filtry do zastosowania przy listowaniu VM
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {"filters": filters or {}}
        super().__init__(
            message_type=MessageType.VM_LIST,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


class VMInfoMessage(Message):
    """Wiadomość żądania informacji o maszynie wirtualnej"""

    def __init__(
        self,
        vm_id: str,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania informacji o VM.

        Args:
            vm_id: Identyfikator maszyny wirtualnej
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {"vm_id": vm_id}
        super().__init__(
            message_type=MessageType.VM_INFO,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


class VMCreateMessage(Message):
    """Wiadomość żądania utworzenia maszyny wirtualnej"""

    def __init__(
        self,
        name: str,
        image: str,
        cpu_cores: int = 2,
        memory: int = 2048,
        disk_size: int = 20,
        network: str = "default",
        hypervisor: str = "kvm",
        additional_config: Dict[str, Any] = None,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania utworzenia VM.

        Args:
            name: Nazwa maszyny wirtualnej
            image: Obraz bazowy do użycia
            cpu_cores: Liczba rdzeni CPU
            memory: Ilość pamięci RAM (MB)
            disk_size: Rozmiar dysku (GB)
            network: Nazwa sieci
            hypervisor: Typ hypervisora (kvm, virtualbox)
            additional_config: Dodatkowa konfiguracja
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {
            "name": name,
            "image": image,
            "cpu_cores": cpu_cores,
            "memory": memory,
            "disk_size": disk_size,
            "network": network,
            "hypervisor": hypervisor,
            "config": additional_config or {},
        }
        super().__init__(
            message_type=MessageType.VM_CREATE,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


class VMStartMessage(Message):
    """Wiadomość żądania uruchomienia maszyny wirtualnej"""

    def __init__(
        self,
        vm_id: str,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania uruchomienia VM.

        Args:
            vm_id: Identyfikator maszyny wirtualnej
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {"vm_id": vm_id}
        super().__init__(
            message_type=MessageType.VM_START,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


class VMStopMessage(Message):
    """Wiadomość żądania zatrzymania maszyny wirtualnej"""

    def __init__(
        self,
        vm_id: str,
        force: bool = False,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania zatrzymania VM.

        Args:
            vm_id: Identyfikator maszyny wirtualnej
            force: Czy wymusić zatrzymanie
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {"vm_id": vm_id, "force": force}
        super().__init__(
            message_type=MessageType.VM_STOP,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


class VMDeleteMessage(Message):
    """Wiadomość żądania usunięcia maszyny wirtualnej"""

    def __init__(
        self,
        vm_id: str,
        delete_disk: bool = True,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania usunięcia VM.

        Args:
            vm_id: Identyfikator maszyny wirtualnej
            delete_disk: Czy usunąć również dysk
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {"vm_id": vm_id, "delete_disk": delete_disk}
        super().__init__(
            message_type=MessageType.VM_DELETE,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


class VMStatusMessage(Message):
    """Wiadomość żądania statusu maszyny wirtualnej"""

    def __init__(
        self,
        vm_id: str,
        message_id: str = None,
        sender_id: str = None,
        receiver_id: str = None,
    ):
        """
        Inicjalizuje wiadomość żądania statusu VM.

        Args:
            vm_id: Identyfikator maszyny wirtualnej
            message_id: Unikalny identyfikator wiadomości
            sender_id: Identyfikator nadawcy
            receiver_id: Identyfikator odbiorcy
        """
        data = {"vm_id": vm_id}
        super().__init__(
            message_type=MessageType.VM_STATUS,
            data=data,
            message_id=message_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
        )


# Klasa do walidacji i przetwarzania wiadomości


class ProtocolHandler:
    """
    Klasa do obsługi protokołu komunikacyjnego.

    Odpowiada za walidację, przetwarzanie i routing wiadomości
    protokołu P2P.
    """

    def __init__(self):
        """Inicjalizuje handler protokołu"""
        # Słownik zarejestrowanych handlerów wiadomości
        self.handlers = {}

        # Rejestruj domyślne handlery
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Rejestruje domyślne handlery wiadomości"""
        # Tutaj można zarejestrować domyślne handlery
        pass

    def register_handler(self, message_type: Union[MessageType, str], handler_func):
        """
        Rejestruje handler dla określonego typu wiadomości.

        Args:
            message_type: Typ wiadomości (enum lub string)
            handler_func: Funkcja obsługująca wiadomość
        """
        if isinstance(message_type, MessageType):
            message_type = message_type.value

        self.handlers[message_type] = handler_func
        logger.debug(f"Zarejestrowano handler dla wiadomości typu '{message_type}'")

    def handle_message(
        self, message: Union[Message, Dict[str, Any], str]
    ) -> Optional[Message]:
        """
        Obsługuje przychodzącą wiadomość.

        Args:
            message: Wiadomość do obsłużenia (obiekt, słownik lub JSON)

        Returns:
            Optional[Message]: Odpowiedź lub None
        """
        # Konwertuj wiadomość do obiektu Message jeśli potrzeba
        if isinstance(message, dict):
            message = Message.from_dict(message)
        elif isinstance(message, str):
            message = Message.from_json(message)

        # Pobierz typ wiadomości
        message_type = message.type

        # Znajdź handler dla danego typu wiadomości
        handler = self.handlers.get(message_type)

        if handler:
            try:
                # Wywołaj handler
                return handler(message)
            except Exception as e:
                logger.error(
                    f"Błąd podczas obsługi wiadomości typu '{message_type}': {e}"
                )
                return message.create_error_response(str(e))
        else:
            logger.warning(f"Brak handlera dla wiadomości typu '{message_type}'")
            return message.create_error_response(
                f"Nieobsługiwany typ wiadomości: {message_type}",
                StatusCode.NOT_IMPLEMENTED,
            )

    def validate_message(
        self, message: Union[Message, Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Waliduje wiadomość protokołu.

        Args:
            message: Wiadomość do walidacji

        Returns:
            Tuple[bool, Optional[str]]: (czy_poprawna, komunikat_błędu)
        """
        # Konwertuj do słownika jeśli to obiekt Message
        if isinstance(message, Message):
            message_dict = message.to_dict()
        else:
            message_dict = message

        # Sprawdź wymagane pola
        required_fields = ["type", "message_id"]
        for field in required_fields:
            if field not in message_dict:
                return False, f"Brak wymaganego pola: {field}"

        # Sprawdź typ wiadomości
        message_type = message_dict["type"]
        valid_types = [mt.value for mt in MessageType]
        if message_type not in valid_types and not message_type.endswith("_response"):
            return False, f"Nieprawidłowy typ wiadomości: {message_type}"

        # Wiadomość jest poprawna
        return True, None


# Inicjalizuj moduł
protocol_handler = ProtocolHandler()
