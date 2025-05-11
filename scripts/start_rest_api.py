#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt uruchamiający serwer REST API jako usługę.

Ten skrypt uruchamia serwer REST API w tle jako usługę,
umożliwiając zarządzanie maszynami wirtualnymi, siecią P2P
i innymi zasobami w środowisku AI Environment Manager.
"""

import os
import sys
import time
import signal
import logging
import argparse
import asyncio
from pathlib import Path
from daemon import DaemonContext
from daemon.pidfile import PIDLockFile

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić importowanie modułów
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api.rest_server import start_server


def setup_logging(log_file, debug=False):
    """
    Konfiguruje system logowania.
    
    Args:
        log_file: Ścieżka do pliku logów
        debug: Czy włączyć tryb debugowania
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Utwórz katalog dla pliku logów, jeśli nie istnieje
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Konfiguracja głównego loggera
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=log_file,
        filemode="a"
    )


def parse_arguments():
    """
    Parsuje argumenty wiersza poleceń.
    
    Returns:
        argparse.Namespace: Sparsowane argumenty
    """
    parser = argparse.ArgumentParser(
        description="Uruchamia serwer REST API jako usługę"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Adres hosta (domyślnie: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port (domyślnie: 8080)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Włącza tryb debugowania"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default="/var/log/twinshare/rest_api.log",
        help="Ścieżka do pliku logów (domyślnie: /var/log/twinshare/rest_api.log)"
    )
    
    parser.add_argument(
        "--pid-file",
        type=str,
        default="/run/twinshare/rest_api.pid",
        help="Ścieżka do pliku PID (domyślnie: /run/twinshare/rest_api.pid)"
    )
    
    parser.add_argument(
        "--foreground",
        action="store_true",
        help="Uruchamia serwer na pierwszym planie (nie jako daemon)"
    )
    
    parser.add_argument(
        "action",
        choices=["start", "stop", "restart", "status"],
        help="Akcja do wykonania"
    )
    
    return parser.parse_args()


def get_pid_from_file(pid_file):
    """
    Pobiera PID z pliku PID.
    
    Args:
        pid_file: Ścieżka do pliku PID
    
    Returns:
        int: PID procesu lub None, jeśli plik nie istnieje
    """
    if not os.path.exists(pid_file):
        return None
    
    try:
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        return pid
    except (IOError, ValueError):
        return None


def is_process_running(pid):
    """
    Sprawdza, czy proces o podanym PID jest uruchomiony.
    
    Args:
        pid: PID procesu
    
    Returns:
        bool: Czy proces jest uruchomiony
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def stop_process(pid):
    """
    Zatrzymuje proces o podanym PID.
    
    Args:
        pid: PID procesu
    
    Returns:
        bool: Czy proces został zatrzymany
    """
    if not is_process_running(pid):
        return True
    
    try:
        # Wyślij sygnał SIGTERM
        os.kill(pid, signal.SIGTERM)
        
        # Poczekaj na zakończenie procesu
        for _ in range(10):
            if not is_process_running(pid):
                return True
            time.sleep(0.5)
        
        # Jeśli proces nadal działa, wyślij sygnał SIGKILL
        os.kill(pid, signal.SIGKILL)
        return True
    except OSError:
        return False


def run_server(host, port, debug, log_file):
    """
    Uruchamia serwer REST API.
    
    Args:
        host: Adres hosta
        port: Port
        debug: Czy włączyć tryb debugowania
        log_file: Ścieżka do pliku logów
    """
    # Konfiguruj logowanie
    setup_logging(log_file, debug)
    
    # Uruchom serwer
    loop = asyncio.get_event_loop()
    server = loop.run_until_complete(start_server(host, port))
    
    # Obsługa sygnałów
    def handle_signal(sig, frame):
        logging.info(f"Otrzymano sygnał {sig}, zatrzymuję serwer...")
        loop.run_until_complete(server.stop())
        loop.stop()
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        # Utrzymuj serwer działający
        loop.run_forever()
    except KeyboardInterrupt:
        # Zatrzymaj serwer po naciśnięciu Ctrl+C
        loop.run_until_complete(server.stop())
    finally:
        loop.close()


def main():
    """Główna funkcja skryptu."""
    args = parse_arguments()
    
    # Utwórz katalog dla pliku PID, jeśli nie istnieje
    pid_dir = os.path.dirname(args.pid_file)
    if pid_dir and not os.path.exists(pid_dir):
        os.makedirs(pid_dir)
    
    # Pobierz PID z pliku PID
    pid = get_pid_from_file(args.pid_file)
    
    # Obsłuż akcję
    if args.action == "status":
        if pid and is_process_running(pid):
            print(f"Serwer REST API jest uruchomiony (PID: {pid})")
            return 0
        else:
            print("Serwer REST API nie jest uruchomiony")
            return 1
    
    elif args.action == "stop":
        if pid and is_process_running(pid):
            print(f"Zatrzymuję serwer REST API (PID: {pid})...")
            if stop_process(pid):
                print("Serwer REST API został zatrzymany")
                if os.path.exists(args.pid_file):
                    os.remove(args.pid_file)
                return 0
            else:
                print("Nie udało się zatrzymać serwera REST API")
                return 1
        else:
            print("Serwer REST API nie jest uruchomiony")
            return 0
    
    elif args.action == "restart":
        if pid and is_process_running(pid):
            print(f"Zatrzymuję serwer REST API (PID: {pid})...")
            if not stop_process(pid):
                print("Nie udało się zatrzymać serwera REST API")
                return 1
            if os.path.exists(args.pid_file):
                os.remove(args.pid_file)
        
        print(f"Uruchamiam serwer REST API na {args.host}:{args.port}...")
    
    elif args.action == "start":
        if pid and is_process_running(pid):
            print(f"Serwer REST API jest już uruchomiony (PID: {pid})")
            return 0
        
        print(f"Uruchamiam serwer REST API na {args.host}:{args.port}...")
    
    # Uruchom serwer
    if args.foreground:
        # Uruchom serwer na pierwszym planie
        run_server(args.host, args.port, args.debug, args.log_file)
    else:
        # Uruchom serwer jako daemon
        with DaemonContext(
            pidfile=PIDLockFile(args.pid_file),
            stdout=None,
            stderr=None,
            detach_process=True
        ):
            run_server(args.host, args.port, args.debug, args.log_file)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
