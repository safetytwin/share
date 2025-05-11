#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł konfiguracyjny dla AI Environment Manager.

Implementuje zarządzanie konfiguracją, wczytywanie ustawień
z plików konfiguracyjnych i zmiennych środowiskowych.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ai-env-manager.core.config")

# Domyślne ścieżki
HOME_DIR = Path.home()
CONFIG_DIR = Path(os.environ.get("AI_ENV_CONFIG_DIR", HOME_DIR / ".ai-environment"))

# Domyślna konfiguracja
DEFAULT_CONFIG = {
    "version": "1.0.0",
    # Ścieżki do katalogów
    "paths": {
        "workspaces": str(CONFIG_DIR / "workspaces"),
        "templates": str(CONFIG_DIR / "templates"),
        "exports": str(CONFIG_DIR / "exports"),
        "vm_images": str(CONFIG_DIR / "vm-images"),
        "docker": str(CONFIG_DIR / "docker"),
        "logs": str(CONFIG_DIR / "logs"),
    },
    # Ustawienia użytkownika
    "user": {"name": "", "email": ""},
    # Ustawienia API
    "api": {
        "port": int(os.environ.get("AI_ENV_API_PORT", 37780)),
        "host": os.environ.get("AI_ENV_API_HOST", "127.0.0.1"),
        "allow_remote": os.environ.get("AI_ENV_API_ALLOW_REMOTE", "false").lower()
        == "true",
        "use_auth": os.environ.get("AI_ENV_API_USE_AUTH", "false").lower() == "true",
        "key": os.environ.get("AI_ENV_API_KEY", ""),
        "use_ssl": False,
        "ssl_cert": "",
        "ssl_key": "",
    },
    # Ustawienia interfejsu webowego
    "web": {
        "port": int(os.environ.get("AI_ENV_WEB_PORT", 8000)),
        "open_browser": os.environ.get("AI_ENV_OPEN_BROWSER", "true").lower() == "true",
        "theme": os.environ.get("AI_ENV_THEME", "light"),  # light, dark, system
    },
    # Ustawienia wykrywania P2P
    "p2p": {
        "discovery": {
            "port": int(os.environ.get("AI_ENV_P2P_PORT", 37777)),
            "broadcast_interval": int(os.environ.get("AI_ENV_P2P_INTERVAL", 10)),
            "enable": os.environ.get("AI_ENV_P2P_ENABLE", "true").lower() == "true",
            "networks": [],  # Lista dozwolonych sieci, np. ["192.168.1.0/24"]
        },
        "node": {
            "name": os.environ.get("AI_ENV_NODE_NAME", ""),
            "id": os.environ.get("AI_ENV_NODE_ID", ""),
            "features": [],  # Funkcje obsługiwane przez ten węzeł
        },
        "network": {
            "ssl": os.environ.get("AI_ENV_P2P_SSL", "false").lower() == "true",
            "cert_file": "",
            "key_file": "",
        },
        "federation": {
            "enabled": os.environ.get("AI_ENV_FEDERATION_ENABLE", "false").lower()
            == "true",
            "token": os.environ.get("AI_ENV_FEDERATION_TOKEN", ""),
        },
    },
    # Ustawienia zasobów
    "resources": {
        "cpu_reservation": int(os.environ.get("AI_ENV_CPU_RESERVATION", 2)),
        "memory_reservation_percent": int(
            os.environ.get("AI_ENV_MEMORY_RESERVATION", 20)
        ),
        "disk_reservation_gb": int(os.environ.get("AI_ENV_DISK_RESERVATION", 20)),
    },
    # Ustawienia środowisk wykonawczych
    "runtime": {
        "vm": {
            "enabled": os.environ.get("AI_ENV_VM_ENABLE", "true").lower() == "true",
            "type": os.environ.get("AI_ENV_VM_TYPE", "kvm"),
            "network": os.environ.get("AI_ENV_VM_NETWORK", "default"),
            "storage_pool": os.environ.get("AI_ENV_VM_STORAGE_POOL", "default"),
        },
        "container": {
            "enabled": os.environ.get("AI_ENV_CONTAINER_ENABLE", "true").lower()
            == "true",
            "type": os.environ.get("AI_ENV_CONTAINER_TYPE", "docker"),
            "compose_version": os.environ.get("AI_ENV_CONTAINER_COMPOSE_VERSION", "v2"),
        },
        "process": {
            "enabled": os.environ.get("AI_ENV_PROCESS_ENABLE", "true").lower() == "true"
        },
    },
    # Ustawienia sieciowe
    "network": {
        "proxy": {
            "http": os.environ.get("http_proxy", ""),
            "https": os.environ.get("https_proxy", ""),
            "no_proxy": os.environ.get("no_proxy", "localhost,127.0.0.1"),
        }
    },
    # Integracje z zewnętrznymi systemami
    "integrations": {
        "git": {
            "provider": os.environ.get("AI_ENV_GIT_PROVIDER", ""),
            "token": os.environ.get("AI_ENV_GIT_TOKEN", ""),
            "username": os.environ.get("AI_ENV_GIT_USERNAME", ""),
        },
        "ci": {
            "provider": os.environ.get("AI_ENV_CI_PROVIDER", ""),
            "url": os.environ.get("AI_ENV_CI_URL", ""),
            "token": os.environ.get("AI_ENV_CI_TOKEN", ""),
        },
    },
    # Ustawienia logowania
    "logging": {
        "level": os.environ.get("AI_ENV_LOG_LEVEL", "INFO"),
        "file": os.environ.get(
            "AI_ENV_LOG_FILE", str(CONFIG_DIR / "logs" / "ai-environment-manager.log")
        ),
        "max_size": int(
            os.environ.get("AI_ENV_LOG_MAX_SIZE", 10 * 1024 * 1024)
        ),  # 10 MB
        "backup_count": int(os.environ.get("AI_ENV_LOG_BACKUP_COUNT", 5)),
    },
}


class Config:
    """
    Klasa do zarządzania konfiguracją systemu.

    Obsługuje wczytywanie konfiguracji z pliku, zapisywanie
    zmian, dostęp do ustawień i zarządzanie domyślnymi wartościami.
    """

    def __init__(self, config_file: Optional[Path] = None):
        """
        Inicjalizuje obiekt konfiguracji.

        Args:
            config_file: Ścieżka do pliku konfiguracyjnego (opcjonalna)
        """
        self.config_file = config_file or (CONFIG_DIR / "config.yaml")
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> bool:
        """
        Wczytuje konfigurację z pliku.

        Returns:
            True jeśli konfiguracja została wczytana pomyślnie, False w przeciwnym razie
        """
        if not self.config_file.exists():
            logger.info(
                f"Plik konfiguracyjny {self.config_file} nie istnieje, tworzenie domyślnej konfiguracji"
            )
            return self.save()

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)

            if loaded_config:
                # Głębokie łączenie załadowanej konfiguracji z domyślną
                self._merge_config(self.config, loaded_config)

            logger.debug(f"Konfiguracja wczytana z {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania konfiguracji: {e}")
            return False

    def save(self) -> bool:
        """
        Zapisuje konfigurację do pliku.

        Returns:
            True jeśli konfiguracja została zapisana pomyślnie, False w przeciwnym razie
        """
        try:
            # Upewnij się, że katalog konfiguracyjny istnieje
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False)

            logger.debug(f"Konfiguracja zapisana do {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        Pobiera wartość z konfiguracji.

        Args:
            key: Klucz konfiguracji (może zawierać kropki dla zagnieżdżonych kluczy)
            default: Domyślna wartość jeśli klucz nie istnieje

        Returns:
            Wartość konfiguracji lub wartość domyślna
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> bool:
        """
        Ustawia wartość w konfiguracji.

        Args:
            key: Klucz konfiguracji (może zawierać kropki dla zagnieżdżonych kluczy)
            value: Wartość do ustawienia

        Returns:
            True jeśli wartość została ustawiona pomyślnie, False w przeciwnym razie
        """
        keys = key.split(".")
        config = self.config

        # Przejdź do właściwego miejsca w konfiguracji
        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                # Jeśli aktualny poziom nie jest słownikiem, zastąp go słownikiem
                config[k] = {}
            config = config[k]

        # Ustaw wartość
        config[keys[-1]] = value

        # Zapisz zmiany
        return self.save()

    def reset(self) -> bool:
        """
        Resetuje konfigurację do wartości domyślnych.

        Returns:
            True jeśli reset się powiódł, False w przeciwnym razie
        """
        self.config = DEFAULT_CONFIG.copy()
        return self.save()

    def copy(self) -> Dict[str, Any]:
        """
        Zwraca kopię aktualnej konfiguracji.

        Returns:
            Kopia konfiguracji
        """
        import copy

        return copy.deepcopy(self.config)

    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> None:
        """
        Głębokie łączenie domyślnej konfiguracji z załadowaną.

        Args:
            default: Domyślna konfiguracja
            loaded: Załadowana konfiguracja
        """
        for key, value in loaded.items():
            if (
                key in default
                and isinstance(default[key], dict)
                and isinstance(value, dict)
            ):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def _safe_config(self) -> Dict[str, Any]:
        """
        Zwraca wersję konfiguracji bez wrażliwych danych.

        Returns:
            Konfiguracja bez wrażliwych danych
        """
        safe_config = self.copy()

        # Ukryj wrażliwe dane
        if "api" in safe_config and "key" in safe_config["api"]:
            safe_config["api"]["key"] = "********" if safe_config["api"]["key"] else ""

        if (
            "p2p" in safe_config
            and "federation" in safe_config["p2p"]
            and "token" in safe_config["p2p"]["federation"]
        ):
            safe_config["p2p"]["federation"]["token"] = (
                "********" if safe_config["p2p"]["federation"]["token"] else ""
            )

        if "integrations" in safe_config:
            if (
                "git" in safe_config["integrations"]
                and "token" in safe_config["integrations"]["git"]
            ):
                safe_config["integrations"]["git"]["token"] = (
                    "********" if safe_config["integrations"]["git"]["token"] else ""
                )

            if (
                "ci" in safe_config["integrations"]
                and "token" in safe_config["integrations"]["ci"]
            ):
                safe_config["integrations"]["ci"]["token"] = (
                    "********" if safe_config["integrations"]["ci"]["token"] else ""
                )

        return safe_config

    def __str__(self) -> str:
        """
        Zwraca tekstową reprezentację konfiguracji.

        Returns:
            Reprezentacja tekstowa
        """
        return yaml.dump(self._safe_config(), default_flow_style=False)


# Globalna instancja konfiguracji
config = Config()


def ensure_directories():
    """
    Tworzy wszystkie wymagane katalogi na podstawie konfiguracji.
    """
    # Utwórz główny katalog konfiguracyjny
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Utwórz wszystkie katalogi z sekcji paths
    for path_name, path_str in config.get("paths", {}).items():
        path = Path(path_str)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Utworzono katalog: {path}")

    # Utwórz katalog na logi
    log_file = Path(
        config.get(
            "logging.file", str(CONFIG_DIR / "logs" / "ai-environment-manager.log")
        )
    )
    log_file.parent.mkdir(parents=True, exist_ok=True)


def configure_logging():
    """
    Konfiguruje system logowania na podstawie ustawień.
    """
    log_level_str = config.get("logging.level", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    log_file = config.get(
        "logging.file", str(CONFIG_DIR / "logs" / "ai-environment-manager.log")
    )
    max_size = config.get("logging.max_size", 10 * 1024 * 1024)  # 10 MB
    backup_count = config.get("logging.backup_count", 5)

    # Konfiguracja głównego loggera
    logger = logging.getLogger("ai-env-manager")
    logger.setLevel(log_level)

    # Usuń istniejące handlery
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Dodaj handler dla konsoli
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)


def initialize():
    """
    Inicjalizuje system konfiguracji.

    Wczytuje konfigurację, tworzy wymagane katalogi i konfiguruje logowanie.
    """
    try:
        # Wczytaj konfigurację
        config.load()

        # Utwórz wymagane katalogi
        ensure_directories()

        # Skonfiguruj logowanie
        configure_logging()

        logger.info("Inicjalizacja konfiguracji zakończona pomyślnie")
        return True
    except Exception as e:
        print(f"Błąd podczas inicjalizacji konfiguracji: {e}")
        logger.error(f"Błąd podczas inicjalizacji konfiguracji: {e}")
        return False


# Automatyczna inicjalizacja przy imporcie
if __name__ != "__main__":
    initialize()
