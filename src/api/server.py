# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serwer REST API dla AI Environment Manager.

Implementuje RESTful API do zarządzania workspace'ami, środowiskami i projektami.
Stanowi warstwę pomiędzy interfejsem użytkownika a logiką biznesową.
"""

import http.server
import json
import logging
import os
import shutil
import socketserver
import threading
import urllib.parse
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import yaml

from ..core.config import config
from ..core.workspace import Workspace
from ..p2p.discovery import discovery
from ..sharing.repository import repository

logger = logging.getLogger("ai-env-manager.api.server")

# Konfiguracja
API_PORT = config.get("api.port", 37780)
API_HOST = config.get("api.host", "127.0.0.1")
ALLOW_REMOTE = config.get("api.allow_remote", False)
USE_AUTH = config.get("api.use_auth", False)
API_KEY = config.get("api.key", None)

# Obsługiwane typy zawartości
CONTENT_TYPES = {
    "json": "application/json",
    "text": "text/plain",
    "html": "text/html",
    "xml": "application/xml",
    "yaml": "application/x-yaml",
}


class APIServer:
    """Implementacja serwera REST API"""

    def __init__(self):
        """Inicjalizuje serwer API"""
        self.running = False
        self.server = None
        self.server_thread = None
        self.host = API_HOST if not ALLOW_REMOTE else "0.0.0.0"
        self.port = API_PORT
        self.endpoints = {}  # URL -> (method, handler)

        # Rejestruj domyślne handlery
        self.register_default_endpoints()

    def start(self) -> bool:
        """Uruchamia serwer API"""
        if self.running:
            logger.info("Serwer API już działa")
            return False

        self.running = True

        # Uruchom serwer HTTP w osobnym wątku
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        logger.info(f"Uruchomiono serwer API na {self.host}:{self.port}")
        return True

    def stop(self) -> bool:
        """Zatrzymuje serwer API"""
        if not self.running:
            logger.info("Serwer API już jest zatrzymany")
            return False

        self.running = False

        # Zatrzymaj serwer HTTP
        if self.server:
            self.server.shutdown()

        # Poczekaj na zakończenie wątku
        if self.server_thread:
            self.server_thread.join(1)

        logger.info("Zatrzymano serwer API")
        return True

    def register_endpoint(self, path: str, method: str, handler: Callable) -> None:
        """
        Rejestruje nowy endpoint API.

        Args:
            path: Ścieżka URL (np. /workspaces)
            method: Metoda HTTP (GET, POST, PUT, DELETE)
            handler: Funkcja obsługująca żądanie
        """
        key = (path, method.upper())
        self.endpoints[key] = handler
        logger.debug(f"Zarejestrowano endpoint: {method} {path}")

    def register_default_endpoints(self) -> None:
        """Rejestruje domyślne endpointy API"""
        # Informacje o API
        self.register_endpoint("/", "GET", self.handle_api_info)

        # Endpointy dla workspace'ów
        self.register_endpoint("/workspaces", "GET", self.handle_list_workspaces)
        self.register_endpoint("/workspaces", "POST", self.handle_create_workspace)
        self.register_endpoint("/workspaces/{name}", "GET", self.handle_get_workspace)
        self.register_endpoint(
            "/workspaces/{name}", "DELETE", self.handle_delete_workspace
        )
        self.register_endpoint(
            "/workspaces/{name}/export", "POST", self.handle_export_workspace
        )
        self.register_endpoint(
            "/workspaces/{name}/start", "POST", self.handle_start_workspace
        )
        self.register_endpoint(
            "/workspaces/{name}/stop", "POST", self.handle_stop_workspace
        )

        # Endpointy dla projektów
        self.register_endpoint(
            "/workspaces/{workspace}/projects", "GET", self.handle_list_projects
        )
        self.register_endpoint(
            "/workspaces/{workspace}/projects", "POST", self.handle_create_project
        )
        self.register_endpoint(
            "/workspaces/{workspace}/projects/{name}", "GET", self.handle_get_project
        )
        self.register_endpoint(
            "/workspaces/{workspace}/projects/{name}",
            "DELETE",
            self.handle_delete_project,
        )

        # Endpointy dla środowisk
        self.register_endpoint(
            "/workspaces/{workspace}/environments", "GET", self.handle_list_environments
        )
        self.register_endpoint(
            "/workspaces/{workspace}/environments",
            "POST",
            self.handle_create_environment,
        )
        self.register_endpoint(
            "/workspaces/{workspace}/environments/{name}",
            "GET",
            self.handle_get_environment,
        )
        self.register_endpoint(
            "/workspaces/{workspace}/environments/{name}",
            "DELETE",
            self.handle_delete_environment,
        )
        self.register_endpoint(
            "/workspaces/{workspace}/environments/{name}/start",
            "POST",
            self.handle_start_environment,
        )
        self.register_endpoint(
            "/workspaces/{workspace}/environments/{name}/stop",
            "POST",
            self.handle_stop_environment,
        )

        # Endpointy dla wykrywania P2P
        self.register_endpoint("/peers", "GET", self.handle_list_peers)
        self.register_endpoint("/peers/{id}", "GET", self.handle_get_peer)

        # Endpointy dla udostępniania
        self.register_endpoint("/shared", "GET", self.handle_list_shared)
        self.register_endpoint(
            "/shared/{workspace}", "POST", self.handle_share_workspace
        )
        self.register_endpoint(
            "/shared/{workspace}", "DELETE", self.handle_unshare_workspace
        )

        # Endpointy dla importu
        self.register_endpoint("/import", "POST", self.handle_import_workspace)

        # Endpointy dla konfiguracji
        self.register_endpoint("/config", "GET", self.handle_get_config)
        self.register_endpoint("/config", "POST", self.handle_update_config)

    def _run_server(self) -> None:
        """Uruchamia serwer HTTP"""
        handler = self._create_request_handler()

        # Znajdź dostępny port
        port = self.port
        while True:
            try:
                self.server = socketserver.ThreadingTCPServer(
                    (self.host, port), handler
                )
                self.port = port
                break
            except OSError:
                port += 1
                if port > self.port + 100:
                    raise Exception("Nie można znaleźć dostępnego portu")

        logger.info(f"Serwer API nasłuchuje na {self.host}:{self.port}")

        try:
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"Błąd podczas działania serwera API: {e}")
        finally:
            self.running = False
            logger.info("Serwer API zatrzymany")

    def _create_request_handler(self):
        """Tworzy handler dla serwera HTTP"""
        api_server = self

        class APIRequestHandler(http.server.BaseHTTPRequestHandler):
            """Handler obsługujący żądania HTTP"""

            def log_message(self, format, *args):
                """Wyłącza domyślne logowanie żądań HTTP"""
                return

            def do_GET(self):
                """Obsługuje żądania GET"""
                self._handle_request("GET")

            def do_POST(self):
                """Obsługuje żądania POST"""
                self._handle_request("POST")

            def do_PUT(self):
                """Obsługuje żądania PUT"""
                self._handle_request("PUT")

            def do_DELETE(self):
                """Obsługuje żądania DELETE"""
                self._handle_request("DELETE")

            def _handle_request(self, method):
                """Obsługuje żądanie HTTP"""
                try:
                    # Parsuj ścieżkę i parametry
                    parsed_url = urllib.parse.urlparse(self.path)
                    path = parsed_url.path

                    # Pobierz parametry zapytania
                    query_params = {}
                    if parsed_url.query:
                        query_params = dict(urllib.parse.parse_qsl(parsed_url.query))

                    # Sprawdź autoryzację jeśli wymagana
                    if USE_AUTH and API_KEY:
                        auth_header = self.headers.get("Authorization")
                        if (
                            not auth_header
                            or not auth_header.startswith("Bearer ")
                            or auth_header[7:] != API_KEY
                        ):
                            self._send_json_response({"error": "Unauthorized"}, 401)
                            return

                        # Pobierz dane z żądania (dla POST, PUT)
                    content_length = int(self.headers.get("Content-Length", 0))
                    request_body = (
                        self.rfile.read(content_length).decode("utf-8")
                        if content_length > 0
                        else ""
                    )

                    if request_body and self.headers.get("Content-Type", "").startswith(
                        "application/json"
                    ):
                        try:
                            request_data = json.loads(request_body)
                        except json.JSONDecodeError:
                            request_data = {}
                    else:
                        request_data = {}

                    # Znajdź handler dla ścieżki i metody
                    handler, path_params = self._find_handler(path, method)

                    if handler:
                        # Wywołaj handler
                        handler_args = {
                            "path_params": path_params,
                            "query_params": query_params,
                            "request_data": request_data,
                            "headers": dict(self.headers),
                        }

                        status_code, content_type, response_data = handler(
                            **handler_args
                        )

                        # Wyślij odpowiedź
                        if content_type == "application/json":
                            self._send_json_response(response_data, status_code)
                        else:
                            self._send_response(
                                response_data, status_code, content_type
                            )
                    else:
                        # Brak handlera dla ścieżki i metody
                        self._send_json_response({"error": "Not Found"}, 404)

                except Exception as e:
                    logger.error(
                        f"Błąd podczas obsługi żądania {method} {self.path}: {e}"
                    )
                    self._send_json_response({"error": str(e)}, 500)

                def _find_handler(
                    self, path: str, method: str
                ) -> Tuple[Optional[Callable], Dict[str, str]]:
                    """Znajduje handler dla ścieżki i metody"""
                    # Najpierw sprawdź dokładne dopasowanie
                    key = (path, method)
                    if key in api_server.endpoints:
                        return api_server.endpoints[key], {}

                    # Jeśli nie znaleziono, sprawdź dopasowanie z parametrami ścieżki
                    path_parts = path.strip("/").split("/")

                    for endpoint_key, handler in api_server.endpoints.items():
                        endpoint_path, endpoint_method = endpoint_key

                        # Sprawdź metodę
                        if endpoint_method != method:
                            continue

                        # Parsuj ścieżkę endpointu
                        endpoint_parts = endpoint_path.strip("/").split("/")

                        # Sprawdź liczbę części ścieżki
                        if len(endpoint_parts) != len(path_parts):
                            continue

                        # Sprawdź dopasowanie części ścieżki
                        match = True
                        path_params = {}

                        for i, (endpoint_part, path_part) in enumerate(
                            zip(endpoint_parts, path_parts)
                        ):
                            if endpoint_part.startswith("{") and endpoint_part.endswith(
                                "}"
                            ):
                                # Parametr ścieżki
                                param_name = endpoint_part[1:-1]
                                path_params[param_name] = path_part
                            elif endpoint_part != path_part:
                                # Niedopasowanie
                                match = False
                                break

                        if match:
                            return handler, path_params

                    return None, {}

                def _send_json_response(
                    self, data: Any, status_code: int = 200
                ) -> None:
                    """Wysyła odpowiedź JSON"""
                    self._send_response(
                        json.dumps(data), status_code, CONTENT_TYPES["json"]
                    )

                def _send_response(
                    self,
                    data: str,
                    status_code: int = 200,
                    content_type: str = CONTENT_TYPES["text"],
                ) -> None:
                    """Wysyła odpowiedź HTTP"""
                    self.send_response(status_code)
                    self.send_header("Content-Type", content_type)
                    self.send_header("Content-Length", str(len(data.encode("utf-8"))))
                    self.end_headers()
                    self.wfile.write(data.encode("utf-8"))

                return APIRequestHandler

                # ===== HANDLERY API =====

                def handle_api_info(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca informacje o API"""
                    info = {
                        "name": "AI Environment Manager API",
                        "version": config.get("version", "1.0.0"),
                        "endpoints": list(
                            set(path for (path, _) in self.endpoints.keys())
                        ),
                        "status": "running" if self.running else "stopped",
                    }
                    return 200, CONTENT_TYPES["json"], info

                def handle_list_workspaces(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca listę workspace'ów"""
                    workspaces = Workspace.list_workspaces()
                    return 200, CONTENT_TYPES["json"], {"workspaces": workspaces}

                def handle_create_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Tworzy nowy workspace"""
                    request_data = kwargs.get("request_data", {})

                    name = request_data.get("name")
                    description = request_data.get("description", "")

                    if not name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required field: name"},
                        )

                    try:
                        workspace = Workspace(name, create_if_missing=True)

                        # Aktualizuj opis
                        if description:
                            workspace.data["description"] = description
                            workspace.save()

                        return (
                            201,
                            CONTENT_TYPES["json"],
                            {
                                "message": f"Workspace {name} created",
                                "workspace": workspace.data,
                            },
                        )
                    except Exception as e:
                        logger.error(f"Error creating workspace {name}: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_get_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca szczegóły workspace'u"""
                    path_params = kwargs.get("path_params", {})
                    name = path_params.get("name")

                    if not name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: name"},
                        )

                    try:
                        workspace = Workspace(name, create_if_missing=False)
                        return 200, CONTENT_TYPES["json"], {"workspace": workspace.data}
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {name}"},
                        )
                    except Exception as e:
                        logger.error(f"Error getting workspace {name}: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_delete_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Usuwa workspace"""
                    path_params = kwargs.get("path_params", {})
                    query_params = kwargs.get("query_params", {})
                    name = path_params.get("name")

                    if not name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: name"},
                        )

                    # Sprawdź czy usunąć dane
                    remove_data = (
                        query_params.get("remove_data", "false").lower() == "true"
                    )

                    try:
                        workspace = Workspace(name, create_if_missing=False)
                        workspace_dir = workspace.path

                        # Utwórz kopię danych jeśli nie usuwamy
                        if not remove_data:
                            data_dir = workspace_dir / "data"
                            if data_dir.exists():
                                backup_dir = (
                                    workspace.workspaces_dir / f"{name}-data-backup"
                                )
                                if backup_dir.exists():
                                    shutil.rmtree(backup_dir)
                                shutil.copytree(data_dir, backup_dir)

                        # Usuń katalog workspace'u
                        shutil.rmtree(workspace_dir)

                        # Przywróć dane jeśli nie usuwamy
                        if not remove_data:
                            backup_dir = (
                                workspace.workspaces_dir / f"{name}-data-backup"
                            )
                            if backup_dir.exists():
                                os.makedirs(workspace_dir / "data", exist_ok=True)
                                shutil.move(backup_dir, workspace_dir / "data")

                        return (
                            200,
                            CONTENT_TYPES["json"],
                            {"message": f"Workspace {name} deleted"},
                        )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {name}"},
                        )
                    except Exception as e:
                        logger.error(f"Error deleting workspace {name}: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_export_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Eksportuje workspace do pliku ZIP"""
                    path_params = kwargs.get("path_params", {})
                    request_data = kwargs.get("request_data", {})
                    name = path_params.get("name")

                    if not name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: name"},
                        )

                    # Opcje eksportu
                    include_data = request_data.get("include_data", True)
                    output_path = request_data.get("output_path")

                    if output_path:
                        output_path = Path(output_path)

                    try:
                        workspace = Workspace(name, create_if_missing=False)
                        result = workspace.export(
                            output_path, include_data=include_data
                        )

                        if result:
                            return (
                                200,
                                CONTENT_TYPES["json"],
                                {
                                    "message": f"Workspace {name} exported",
                                    "path": str(result),
                                },
                            )
                        else:
                            return (
                                500,
                                CONTENT_TYPES["json"],
                                {"error": f"Failed to export workspace {name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {name}"},
                        )
                    except Exception as e:
                        logger.error(f"Error exporting workspace {name}: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_start_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Uruchamia workspace"""
                    path_params = kwargs.get("path_params", {})
                    name = path_params.get("name")

                    if not name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: name"},
                        )

                    try:
                        workspace = Workspace(name, create_if_missing=False)

                        # Aktualizuj status
                        workspace.update_status("running")

                        # TODO: Uruchom środowiska w workspace'ie

                        return (
                            200,
                            CONTENT_TYPES["json"],
                            {"message": f"Workspace {name} started"},
                        )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {name}"},
                        )
                    except Exception as e:
                        logger.error(f"Error starting workspace {name}: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_stop_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zatrzymuje workspace"""
                    path_params = kwargs.get("path_params", {})
                    name = path_params.get("name")

                    if not name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: name"},
                        )

                    try:
                        workspace = Workspace(name, create_if_missing=False)

                        # Aktualizuj status
                        workspace.update_status("stopped")

                        # TODO: Zatrzymaj środowiska w workspace'ie

                        return (
                            200,
                            CONTENT_TYPES["json"],
                            {"message": f"Workspace {name} stopped"},
                        )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {name}"},
                        )
                    except Exception as e:
                        logger.error(f"Error stopping workspace {name}: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_list_projects(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca listę projektów w workspace'ie"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")

                    if not workspace_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: workspace"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        projects = []

                        for project_name in workspace.data.get("projects", []):
                            project_data = workspace.get_project(project_name)
                            if project_data:
                                projects.append(project_data)

                        return 200, CONTENT_TYPES["json"], {"projects": projects}
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error listing projects for workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_create_project(self, **kwargs) -> Tuple[int, str, Any]:
                    """Tworzy nowy projekt w workspace'ie"""
                    path_params = kwargs.get("path_params", {})
                    request_data = kwargs.get("request_data", {})
                    workspace_name = path_params.get("workspace")

                    if not workspace_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: workspace"},
                        )

                    project_name = request_data.get("name")
                    if not project_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required field: name"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        result = workspace.add_project(project_name, request_data)

                        if result:
                            return (
                                201,
                                CONTENT_TYPES["json"],
                                {
                                    "message": f"Project {project_name} created in workspace {workspace_name}",
                                    "project": workspace.get_project(project_name),
                                },
                            )
                        else:
                            return (
                                400,
                                CONTENT_TYPES["json"],
                                {"error": f"Failed to create project {project_name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error creating project {project_name} in workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_get_project(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca szczegóły projektu"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")
                    project_name = path_params.get("name")

                    if not workspace_name or not project_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameters"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        project_data = workspace.get_project(project_name)

                        if project_data:
                            return 200, CONTENT_TYPES["json"], {"project": project_data}
                        else:
                            return (
                                404,
                                CONTENT_TYPES["json"],
                                {"error": f"Project not found: {project_name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error getting project {project_name} from workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_delete_project(self, **kwargs) -> Tuple[int, str, Any]:
                    """Usuwa projekt z workspace'u"""
                    path_params = kwargs.get("path_params", {})
                    query_params = kwargs.get("query_params", {})
                    workspace_name = path_params.get("workspace")
                    project_name = path_params.get("name")

                    if not workspace_name or not project_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameters"},
                        )

                    # Sprawdź czy usunąć dane
                    remove_data = (
                        query_params.get("remove_data", "false").lower() == "true"
                    )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        result = workspace.remove_project(
                            project_name, remove_data=remove_data
                        )

                        if result:
                            return (
                                200,
                                CONTENT_TYPES["json"],
                                {"message": f"Project {project_name} deleted"},
                            )
                        else:
                            return (
                                404,
                                CONTENT_TYPES["json"],
                                {"error": f"Project not found: {project_name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error deleting project {project_name} from workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_list_environments(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca listę środowisk w workspace'ie"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")

                    if not workspace_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: workspace"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        environments = []

                        for env_name in workspace.data.get("environments", []):
                            env_data = workspace.get_environment(env_name)
                            if env_data:
                                environments.append(env_data)

                        return (
                            200,
                            CONTENT_TYPES["json"],
                            {"environments": environments},
                        )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error listing environments for workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_create_environment(self, **kwargs) -> Tuple[int, str, Any]:
                    """Tworzy nowe środowisko w workspace'ie"""
                    path_params = kwargs.get("path_params", {})
                    request_data = kwargs.get("request_data", {})
                    workspace_name = path_params.get("workspace")

                    if not workspace_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: workspace"},
                        )

                    env_name = request_data.get("name")
                    if not env_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required field: name"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        result = workspace.add_environment(env_name, request_data)

                        if result:
                            return (
                                201,
                                CONTENT_TYPES["json"],
                                {
                                    "message": f"Environment {env_name} created in workspace {workspace_name}",
                                    "environment": workspace.get_environment(env_name),
                                },
                            )
                        else:
                            return (
                                400,
                                CONTENT_TYPES["json"],
                                {"error": f"Failed to create environment {env_name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error creating environment {env_name} in workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_get_environment(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca szczegóły środowiska"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")
                    env_name = path_params.get("name")

                    if not workspace_name or not env_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameters"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        env_data = workspace.get_environment(env_name)

                        if env_data:
                            return 200, CONTENT_TYPES["json"], {"environment": env_data}
                        else:
                            return (
                                404,
                                CONTENT_TYPES["json"],
                                {"error": f"Environment not found: {env_name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error getting environment {env_name} from workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_delete_environment(self, **kwargs) -> Tuple[int, str, Any]:
                    """Usuwa środowisko z workspace'u"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")
                    env_name = path_params.get("name")

                    if not workspace_name or not env_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameters"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        result = workspace.remove_environment(env_name)

                        if result:
                            return (
                                200,
                                CONTENT_TYPES["json"],
                                {"message": f"Environment {env_name} deleted"},
                            )
                        else:
                            return (
                                404,
                                CONTENT_TYPES["json"],
                                {"error": f"Environment not found: {env_name}"},
                            )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error deleting environment {env_name} from workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_start_environment(self, **kwargs) -> Tuple[int, str, Any]:
                    """Uruchamia środowisko"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")
                    env_name = path_params.get("name")

                    if not workspace_name or not env_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameters"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        env_data = workspace.get_environment(env_name)

                        if not env_data:
                            return (
                                404,
                                CONTENT_TYPES["json"],
                                {"error": f"Environment not found: {env_name}"},
                            )

                        # TODO: Uruchom środowisko

                        # Zaktualizuj status środowiska
                        env_data["status"] = "running"
                        env_data["updated_at"] = datetime.now().isoformat()

                        # Zapisz aktualizację
                        workspace.add_environment(env_name, env_data)

                        return (
                            200,
                            CONTENT_TYPES["json"],
                            {
                                "message": f"Environment {env_name} started",
                                "environment": env_data,
                            },
                        )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error starting environment {env_name} in workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_stop_environment(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zatrzymuje środowisko"""
                    path_params = kwargs.get("path_params", {})
                    workspace_name = path_params.get("workspace")
                    env_name = path_params.get("name")

                    if not workspace_name or not env_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameters"},
                        )

                    try:
                        workspace = Workspace(workspace_name, create_if_missing=False)
                        env_data = workspace.get_environment(env_name)

                        if not env_data:
                            return (
                                404,
                                CONTENT_TYPES["json"],
                                {"error": f"Environment not found: {env_name}"},
                            )

                        # TODO: Zatrzymaj środowisko

                        # Zaktualizuj status środowiska
                        env_data["status"] = "stopped"
                        env_data["updated_at"] = datetime.now().isoformat()

                        # Zapisz aktualizację
                        workspace.add_environment(env_name, env_data)

                        return (
                            200,
                            CONTENT_TYPES["json"],
                            {
                                "message": f"Environment {env_name} stopped",
                                "environment": env_data,
                            },
                        )
                    except FileNotFoundError:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Workspace not found: {workspace_name}"},
                        )
                    except Exception as e:
                        logger.error(
                            f"Error stopping environment {env_name} in workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_list_peers(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca listę węzłów P2P"""
                    peers = discovery.get_peers()
                    return 200, CONTENT_TYPES["json"], {"peers": peers}

                def handle_get_peer(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca informacje o węźle P2P"""
                    path_params = kwargs.get("path_params", {})
                    peer_id = path_params.get("id")

                    if not peer_id:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: id"},
                        )

                    peer = discovery.get_peer(peer_id)

                    if peer:
                        return 200, CONTENT_TYPES["json"], {"peer": peer}
                    else:
                        return (
                            404,
                            CONTENT_TYPES["json"],
                            {"error": f"Peer not found: {peer_id}"},
                        )

                def handle_list_shared(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca listę udostępnionych workspace'ów"""
                    shared = repository.list_shared_workspaces()
                    return 200, CONTENT_TYPES["json"], {"shared": shared}

                def handle_share_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Udostępnia workspace"""
                    path_params = kwargs.get("path_params", {})
                    request_data = kwargs.get("request_data", {})
                    workspace_name = path_params.get("workspace")

                    if not workspace_name:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required parameter: workspace"},
                        )

                    # Opcje udostępniania
                    enable = request_data.get("enable", True)

                    try:
                        result = repository.share_workspace(workspace_name, enable)

                        if result:
                            return (
                                200,
                                CONTENT_TYPES["json"],
                                {
                                    "message": f"Workspace {workspace_name} {'shared' if enable else 'unshared'}"
                                },
                            )
                        else:
                            return (
                                400,
                                CONTENT_TYPES["json"],
                                {
                                    "error": f"Failed to {'share' if enable else 'unshare'} workspace {workspace_name}"
                                },
                            )
                    except Exception as e:
                        logger.error(
                            f"Error {'sharing' if enable else 'unsharing'} workspace {workspace_name}: {e}"
                        )
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_unshare_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Przestaje udostępniać workspace"""
                    kwargs["request_data"] = {"enable": False}
                    return self.handle_share_workspace(**kwargs)

                def handle_import_workspace(self, **kwargs) -> Tuple[int, str, Any]:
                    """Importuje workspace z pliku"""
                    request_data = kwargs.get("request_data", {})

                    file_path = request_data.get("file_path")
                    workspace_name = request_data.get("workspace_name")
                    force_overwrite = request_data.get("force_overwrite", False)

                    if not file_path:
                        return (
                            400,
                            CONTENT_TYPES["json"],
                            {"error": "Missing required field: file_path"},
                        )

                    try:
                        workspace = Workspace.import_from_file(
                            file_path, workspace_name, force_overwrite
                        )

                        if workspace:
                            return (
                                200,
                                CONTENT_TYPES["json"],
                                {
                                    "message": f"Workspace imported as {workspace.name}",
                                    "workspace": workspace.data,
                                },
                            )
                        else:
                            return (
                                500,
                                CONTENT_TYPES["json"],
                                {"error": "Failed to import workspace"},
                            )
                    except Exception as e:
                        logger.error(f"Error importing workspace: {e}")
                        return 500, CONTENT_TYPES["json"], {"error": str(e)}

                def handle_get_config(self, **kwargs) -> Tuple[int, str, Any]:
                    """Zwraca konfigurację systemu"""
                    # Usuń wrażliwe dane
                    safe_config = config.copy()

                    if "api_key" in safe_config:
                        safe_config["api_key"] = "********"

                    if "tokens" in safe_config:
                        safe_config["tokens"] = {
                            k: "********" for k in safe_config["tokens"].keys()
                        }

                    return (200,)  # Moduł API Server (`src/api/server.py`)
