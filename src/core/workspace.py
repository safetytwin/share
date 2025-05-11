#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł workspace'ów dla AI Environment Manager.

Implementuje model workspace'u, który jest kontenerem
dla projektów, środowisk i konfiguracji.
"""

import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .config import config

logger = logging.getLogger("ai-env-manager.core.workspace")


class Workspace:
    """
    Reprezentuje workspace, który jest podstawowym kontenerem
    dla projektów i środowisk AI.
    """

    def __init__(
        self, name: str, path: Optional[Path] = None, create_if_missing: bool = True
    ):
        """
        Inicjalizuje workspace.

        Args:
            name: Nazwa workspace'u
            path: Ścieżka do katalogu workspace'u (opcjonalna)
            create_if_missing: Czy tworzyć workspace jeśli nie istnieje
        """
        self.name = name
        self.workspaces_dir = Path(
            config.get("paths.workspaces", config.CONFIG_DIR / "workspaces")
        )
        self.path = path or (self.workspaces_dir / name)
        self.config_path = self.path / "workspace.yaml"

        # Załaduj lub utwórz konfigurację
        if self.config_path.exists():
            self.data = self._load_config()
        elif create_if_missing:
            self.data = self._create_default_config()
            self.save()
        else:
            raise FileNotFoundError(f"Workspace '{name}' nie istnieje")

    def _load_config(self) -> Dict[str, Any]:
        """Wczytuje konfigurację workspace'u z pliku"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            logger.debug(f"Wczytano konfigurację workspace'u: {self.name}")
            return data
        except Exception as e:
            logger.error(
                f"Błąd podczas wczytywania konfiguracji workspace'u {self.name}: {e}"
            )
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Tworzy domyślną konfigurację workspace'u"""
        return {
            "name": self.name,
            "id": str(uuid.uuid4()),
            "description": f"Workspace {self.name}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "projects": [],
            "environments": [],
            "resources": {
                "cpu_allocation": {},
                "memory_allocation": {},
                "disk_allocation": {},
            },
            "network": {"domain": f"{self.name}.local", "proxy_port": 0},
            "status": "stopped",
            "metadata": {},
            "tags": [],
            "version": "1.0.0",
        }

    def save(self) -> bool:
        """Zapisuje konfigurację workspace'u"""
        try:
            # Utwórz katalogi jeśli nie istnieją
            self.path.mkdir(parents=True, exist_ok=True)
            (self.path / "projects").mkdir(exist_ok=True)
            (self.path / "environments").mkdir(exist_ok=True)
            (self.path / "data").mkdir(exist_ok=True)

            # Aktualizuj timestamp
            self.data["updated_at"] = datetime.now().isoformat()

            # Zapisz konfigurację
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False)

            logger.debug(f"Zapisano konfigurację workspace'u: {self.name}")
            return True
        except Exception as e:
            logger.error(
                f"Błąd podczas zapisywania konfiguracji workspace'u {self.name}: {e}"
            )
            return False

    def export(
        self, output_path: Optional[Path] = None, include_data: bool = True
    ) -> Optional[Path]:
        """
        Eksportuje workspace do pliku ZIP.

        Args:
            output_path: Ścieżka docelowa pliku ZIP (opcjonalna)
            include_data: Czy dołączać dane projektów (domyślnie: True)

        Returns:
            Ścieżka do pliku ZIP lub None w przypadku błędu
        """
        if not self.path.exists():
            logger.error(f"Workspace {self.name} nie istnieje")
            return None

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            exports_dir = Path(
                config.get("paths.exports", config.CONFIG_DIR / "exports")
            )
            exports_dir.mkdir(parents=True, exist_ok=True)
            output_path = exports_dir / f"{self.name}-{timestamp}.zip"

        try:
            # Utwórz katalog tymczasowy
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)

                # Skopiuj pliki konfiguracyjne
                shutil.copy2(self.config_path, temp_dir_path / "workspace.yaml")

                # Skopiuj projekty
                projects_dir = self.path / "projects"
                if projects_dir.exists():
                    projects_target = temp_dir_path / "projects"
                    projects_target.mkdir(exist_ok=True)
                    for project_file in projects_dir.glob("*.yaml"):
                        shutil.copy2(project_file, projects_target)

                # Skopiuj środowiska
                environments_dir = self.path / "environments"
                if environments_dir.exists():
                    environments_target = temp_dir_path / "environments"
                    environments_target.mkdir(exist_ok=True)
                    for env_file in environments_dir.glob("*.yaml"):
                        shutil.copy2(env_file, environments_target)

                # Skopiuj dane projektów jeśli wymagane
                if include_data:
                    data_dir = self.path / "data"
                    if data_dir.exists():
                        data_target = temp_dir_path / "data"
                        data_target.mkdir(exist_ok=True)
                        for item in data_dir.iterdir():
                            if item.is_dir():
                                shutil.copytree(item, data_target / item.name)
                            else:
                                shutil.copy2(item, data_target)

                # Utwórz plik README
                self._create_readme(temp_dir_path)

                # Spakuj wszystko do archiwum ZIP
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.make_archive(str(output_path.with_suffix("")), "zip", temp_dir)

            logger.info(f"Workspace {self.name} został wyeksportowany do {output_path}")
            return output_path.with_suffix(".zip")

        except Exception as e:
            logger.error(f"Błąd podczas eksportowania workspace'u {self.name}: {e}")
            return None

    def _create_readme(self, target_dir: Path) -> None:
        """
        Tworzy plik README.md z informacjami o workspace'ie

        Args:
            target_dir: Katalog docelowy
        """
        readme_path = target_dir / "README.md"

        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(f"# Workspace: {self.name}\n\n")
                f.write(f"**Opis:** {self.data.get('description', 'Brak opisu')}\n\n")
                f.write(f"**Data utworzenia:** {self.data.get('created_at', '')}\n")
                f.write(f"**Data aktualizacji:** {self.data.get('updated_at', '')}\n\n")

                # Dodaj informacje o projektach
                f.write("## Projekty\n\n")
                for project_name in self.data.get("projects", []):
                    project_path = self.path / "projects" / f"{project_name}.yaml"
                    if project_path.exists():
                        try:
                            with open(project_path, "r", encoding="utf-8") as pf:
                                project_data = yaml.safe_load(pf)
                                description = project_data.get(
                                    "description", "Brak opisu"
                                )
                                languages = ", ".join(project_data.get("languages", []))
                                f.write(f"- **{project_name}**: {description}\n")
                                if languages:
                                    f.write(f"  - Języki: {languages}\n")
                        except Exception as e:
                            f.write(f"- **{project_name}**\n")

                # Dodaj informacje o środowiskach
                f.write("\n## Środowiska\n\n")
                for env_name in self.data.get("environments", []):
                    env_path = self.path / "environments" / f"{env_name}.yaml"
                    if env_path.exists():
                        try:
                            with open(env_path, "r", encoding="utf-8") as ef:
                                env_data = yaml.safe_load(ef)
                                description = env_data.get("description", "Brak opisu")
                                env_type = env_data.get("type", "Nieznany")
                                f.write(
                                    f"- **{env_name}** ({env_type}): {description}\n"
                                )
                        except Exception as e:
                            f.write(f"- **{env_name}**\n")

                # Dodaj instrukcję importu
                f.write("\n## Instrukcja importu\n\n")
                f.write("Aby zaimportować ten workspace:\n\n")
                f.write("1. Uruchom AI Environment Manager\n")
                f.write('2. Wybierz opcję "Importuj workspace"\n')
                f.write("3. Wskaż plik ZIP z workspace'm\n")
                f.write("4. Workspace zostanie skonfigurowany automatycznie\n\n")

                # Dodaj informacje o wymaganiach
                f.write("## Wymagania\n\n")

                # Oblicz wymagania na podstawie środowisk
                cpu_req = 0
                memory_req = 0
                disk_req = 0

                for env_name in self.data.get("environments", []):
                    env_path = self.path / "environments" / f"{env_name}.yaml"
                    if env_path.exists():
                        try:
                            with open(env_path, "r", encoding="utf-8") as ef:
                                env_data = yaml.safe_load(ef)
                                resources = env_data.get("resources", {})
                                cpu_req += resources.get("cpu", 1)
                                memory_req += resources.get("memory", 1024)
                                disk_req += resources.get("disk", 5)
                        except Exception:
                            pass

                # Zapewnij minimalne wymagania
                cpu_req = max(cpu_req, 1)
                memory_req = max(memory_req, 1024)
                disk_req = max(disk_req, 5)

                f.write(f"- CPU: minimum {cpu_req} rdzeni\n")
                f.write(f"- RAM: minimum {memory_req / 1024:.1f} GB\n")
                f.write(f"- Dysk: minimum {disk_req} GB\n")

                # Dodaj informacje o wersji
                f.write(f"\n---\n")
                f.write(
                    f"Wyeksportowano przez AI Environment Manager v{config.get('version', '1.0.0')}\n"
                )
                f.write(
                    f"Data eksportu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )

        except Exception as e:
            logger.error(f"Błąd podczas tworzenia pliku README: {e}")

    @classmethod
    def import_from_file(
        cls,
        zip_path: Union[str, Path],
        workspace_name: Optional[str] = None,
        force_overwrite: bool = False,
    ) -> Optional["Workspace"]:
        """
        Importuje workspace z pliku ZIP.

        Args:
            zip_path: Ścieżka do pliku ZIP
            workspace_name: Opcjonalna nazwa dla zaimportowanego workspace'u
            force_overwrite: Czy nadpisać istniejący workspace

        Returns:
            Obiekt Workspace lub None w przypadku błędu
        """
        zip_path = Path(zip_path)

        if not zip_path.exists():
            logger.error(f"Plik {zip_path} nie istnieje")
            return None

        try:
            # Utwórz katalog tymczasowy
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)

                # Rozpakuj archiwum
                shutil.unpack_archive(zip_path, temp_dir_path, "zip")

                # Wczytaj konfigurację workspace'u
                workspace_config_path = temp_dir_path / "workspace.yaml"
                if not workspace_config_path.exists():
                    logger.error(
                        f"Nie znaleziono pliku konfiguracyjnego workspace'u w {zip_path}"
                    )
                    return None

                with open(workspace_config_path, "r", encoding="utf-8") as f:
                    workspace_data = yaml.safe_load(f)

                # Ustaw nazwę workspace'u
                original_name = workspace_data.get("name", "imported-workspace")
                new_name = workspace_name or original_name

                # Sprawdź czy workspace o takiej nazwie już istnieje
                workspaces_dir = Path(
                    config.get("paths.workspaces", config.CONFIG_DIR / "workspaces")
                )
                target_dir = workspaces_dir / new_name

                if target_dir.exists():
                    if force_overwrite:
                        logger.warning(f"Nadpisuję istniejący workspace {new_name}")
                        shutil.rmtree(target_dir)
                    else:
                        # Dodaj timestamp do nazwy
                        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                        new_name = f"{new_name}-{timestamp}"
                        target_dir = workspaces_dir / new_name
                        logger.warning(
                            f"Workspace {original_name} zostanie zaimportowany jako {new_name}"
                        )

                # Zaktualizuj nazwę w konfiguracji
                workspace_data["name"] = new_name
                workspace_data["imported_from"] = original_name
                workspace_data["imported_at"] = datetime.now().isoformat()

                # Utwórz katalogi workspace'u
                target_dir.mkdir(parents=True, exist_ok=True)
                (target_dir / "projects").mkdir(exist_ok=True)
                (target_dir / "environments").mkdir(exist_ok=True)
                (target_dir / "data").mkdir(exist_ok=True)

                # Zapisz zaktualizowaną konfigurację
                with open(target_dir / "workspace.yaml", "w", encoding="utf-8") as f:
                    yaml.dump(workspace_data, f, default_flow_style=False)

                # Skopiuj projekty
                projects_dir = temp_dir_path / "projects"
                if projects_dir.exists():
                    for project_file in projects_dir.glob("*.yaml"):
                        shutil.copy2(project_file, target_dir / "projects")

                # Skopiuj środowiska
                environments_dir = temp_dir_path / "environments"
                if environments_dir.exists():
                    for env_file in environments_dir.glob("*.yaml"):
                        shutil.copy2(env_file, target_dir / "environments")

                # Skopiuj dane
                data_dir = temp_dir_path / "data"
                if data_dir.exists():
                    for item in data_dir.iterdir():
                        if item.is_dir():
                            shutil.copytree(
                                item,
                                target_dir / "data" / item.name,
                                dirs_exist_ok=True,
                            )
                        else:
                            shutil.copy2(item, target_dir / "data")

                logger.info(f"Workspace został zaimportowany jako {new_name}")

                # Zwróć obiekt workspace'u
                return cls(new_name)

        except Exception as e:
            logger.error(f"Błąd podczas importowania workspace'u: {e}")
            return None

    def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera konfigurację projektu.

        Args:
            project_name: Nazwa projektu

        Returns:
            Dane projektu lub None jeśli projekt nie istnieje
        """
        if project_name not in self.data.get("projects", []):
            logger.warning(
                f"Projekt {project_name} nie istnieje w workspace'ie {self.name}"
            )
            return None

        project_path = self.path / "projects" / f"{project_name}.yaml"
        if not project_path.exists():
            logger.warning(f"Plik konfiguracyjny projektu {project_name} nie istnieje")
            return None

        try:
            with open(project_path, "r", encoding="utf-8") as f:
                project_data = yaml.safe_load(f)

            return project_data
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania projektu {project_name}: {e}")
            return None

    def get_environment(self, env_name: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera konfigurację środowiska.

        Args:
            env_name: Nazwa środowiska

        Returns:
            Dane środowiska lub None jeśli środowisko nie istnieje
        """
        if env_name not in self.data.get("environments", []):
            logger.warning(
                f"Środowisko {env_name} nie istnieje w workspace'ie {self.name}"
            )
            return None

        env_path = self.path / "environments" / f"{env_name}.yaml"
        if not env_path.exists():
            logger.warning(f"Plik konfiguracyjny środowiska {env_name} nie istnieje")
            return None

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                env_data = yaml.safe_load(f)

            return env_data
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania środowiska {env_name}: {e}")
            return None

    def add_project(self, project_name: str, project_data: Dict[str, Any]) -> bool:
        """
        Dodaje nowy projekt do workspace'u.

        Args:
            project_name: Nazwa projektu
            project_data: Dane projektu

        Returns:
            True jeśli projekt został dodany pomyślnie, False w przeciwnym razie
        """
        if project_name in self.data.get("projects", []):
            logger.warning(
                f"Projekt {project_name} już istnieje w workspace'ie {self.name}"
            )
            return False

        # Sprawdź czy projekt zawiera wymagane pola
        if "name" not in project_data:
            project_data["name"] = project_name

        if "created_at" not in project_data:
            project_data["created_at"] = datetime.now().isoformat()

        if "updated_at" not in project_data:
            project_data["updated_at"] = datetime.now().isoformat()

        # Zapisz konfigurację projektu
        projects_dir = self.path / "projects"
        projects_dir.mkdir(exist_ok=True)

        project_path = projects_dir / f"{project_name}.yaml"

        try:
            with open(project_path, "w", encoding="utf-8") as f:
                yaml.dump(project_data, f, default_flow_style=False)

            # Zaktualizuj listę projektów
            if "projects" not in self.data:
                self.data["projects"] = []

            if project_name not in self.data["projects"]:
                self.data["projects"].append(project_name)

            # Zapisz konfigurację workspace'u
            self.save()

            # Utwórz katalog dla danych projektu
            (self.path / "data" / project_name).mkdir(exist_ok=True)

            logger.info(f"Dodano projekt {project_name} do workspace'u {self.name}")
            return True

        except Exception as e:
            logger.error(f"Błąd podczas dodawania projektu {project_name}: {e}")
            return False

    def add_environment(self, env_name: str, env_data: Dict[str, Any]) -> bool:
        """
        Dodaje nowe środowisko do workspace'u.

        Args:
            env_name: Nazwa środowiska
            env_data: Dane środowiska

        Returns:
            True jeśli środowisko zostało dodane pomyślnie, False w przeciwnym razie
        """
        if env_name in self.data.get("environments", []):
            logger.warning(
                f"Środowisko {env_name} już istnieje w workspace'ie {self.name}"
            )
            return False

        # Sprawdź czy środowisko zawiera wymagane pola
        if "name" not in env_data:
            env_data["name"] = env_name

        if "created_at" not in env_data:
            env_data["created_at"] = datetime.now().isoformat()

        if "updated_at" not in env_data:
            env_data["updated_at"] = datetime.now().isoformat()

        # Zapisz konfigurację środowiska
        environments_dir = self.path / "environments"
        environments_dir.mkdir(exist_ok=True)

        env_path = environments_dir / f"{env_name}.yaml"

        try:
            with open(env_path, "w", encoding="utf-8") as f:
                yaml.dump(env_data, f, default_flow_style=False)

            # Zaktualizuj listę środowisk
            if "environments" not in self.data:
                self.data["environments"] = []

            if env_name not in self.data["environments"]:
                self.data["environments"].append(env_name)

            # Zapisz konfigurację workspace'u
            self.save()

            logger.info(f"Dodano środowisko {env_name} do workspace'u {self.name}")
            return True

        except Exception as e:
            logger.error(f"Błąd podczas dodawania środowiska {env_name}: {e}")
            return False

    def remove_project(self, project_name: str, remove_data: bool = False) -> bool:
        """
        Usuwa projekt z workspace'u.

        Args:
            project_name: Nazwa projektu
            remove_data: Czy usunąć dane projektu

        Returns:
            True jeśli projekt został usunięty pomyślnie, False w przeciwnym razie
        """
        if project_name not in self.data.get("projects", []):
            logger.warning(
                f"Projekt {project_name} nie istnieje w workspace'ie {self.name}"
            )
            return False

        # Usuń plik konfiguracyjny projektu
        project_path = self.path / "projects" / f"{project_name}.yaml"

        try:
            if project_path.exists():
                project_path.unlink()

            # Usuń dane projektu jeśli wymagane
            if remove_data:
                project_data_dir = self.path / "data" / project_name
                if project_data_dir.exists():
                    shutil.rmtree(project_data_dir)

            # Zaktualizuj listę projektów
            self.data["projects"].remove(project_name)

            # Zapisz konfigurację workspace'u
            self.save()

            logger.info(f"Usunięto projekt {project_name} z workspace'u {self.name}")
            return True

        except Exception as e:
            logger.error(f"Błąd podczas usuwania projektu {project_name}: {e}")
            return False

    def remove_environment(self, env_name: str) -> bool:
        """
        Usuwa środowisko z workspace'u.

        Args:
            env_name: Nazwa środowiska

        Returns:
            True jeśli środowisko zostało usunięte pomyślnie, False w przeciwnym razie
        """
        if env_name not in self.data.get("environments", []):
            logger.warning(
                f"Środowisko {env_name} nie istnieje w workspace'ie {self.name}"
            )
            return False

        # Usuń plik konfiguracyjny środowiska
        env_path = self.path / "environments" / f"{env_name}.yaml"

        try:
            if env_path.exists():
                env_path.unlink()

            # Zaktualizuj listę środowisk
            self.data["environments"].remove(env_name)

            # Zapisz konfigurację workspace'u
            self.save()

            logger.info(f"Usunięto środowisko {env_name} z workspace'u {self.name}")
            return True

        except Exception as e:
            logger.error(f"Błąd podczas usuwania środowiska {env_name}: {e}")
            return False

    def update_status(self, status: str) -> bool:
        """
        Aktualizuje status workspace'u.

        Args:
            status: Nowy status (running, stopped, paused, error)

        Returns:
            True jeśli status został zaktualizowany pomyślnie, False w przeciwnym razie
        """
        valid_statuses = ["running", "stopped", "paused", "error"]

        if status not in valid_statuses:
            logger.warning(f"Nieprawidłowy status: {status}")
            return False

        try:
            self.data["status"] = status
            self.data["updated_at"] = datetime.now().isoformat()

            # Zapisz konfigurację
            self.save()

            logger.info(f"Zaktualizowano status workspace'u {self.name} na {status}")
            return True

        except Exception as e:
            logger.error(
                f"Błąd podczas aktualizacji statusu workspace'u {self.name}: {e}"
            )
            return False

    @classmethod
    def list_workspaces(cls) -> List[Dict[str, Any]]:
        """
        Pobiera listę wszystkich dostępnych workspace'ów.

        Returns:
            Lista danych workspace'ów
        """
        workspaces = []
        workspaces_dir = Path(
            config.get("paths.workspaces", config.CONFIG_DIR / "workspaces")
        )

        if not workspaces_dir.exists():
            return workspaces

        for workspace_dir in workspaces_dir.iterdir():
            if workspace_dir.is_dir():
                workspace_file = workspace_dir / "workspace.yaml"

                if workspace_file.exists():
                    try:
                        with open(workspace_file, "r", encoding="utf-8") as f:
                            workspace_data = yaml.safe_load(f)

                        workspaces.append(
                            {
                                "name": workspace_dir.name,
                                "description": workspace_data.get("description", ""),
                                "created_at": workspace_data.get("created_at", ""),
                                "updated_at": workspace_data.get("updated_at", ""),
                                "status": workspace_data.get("status", "stopped"),
                                "projects": len(workspace_data.get("projects", [])),
                                "environments": len(
                                    workspace_data.get("environments", [])
                                ),
                                "tags": workspace_data.get("tags", []),
                            }
                        )

                    except Exception as e:
                        logger.error(
                            f"Błąd podczas wczytywania workspace'u {workspace_dir.name}: {e}"
                        )

        return workspaces

    def __str__(self) -> str:
        """Zwraca tekstową reprezentację workspace'u"""
        return f"Workspace({self.name}, status={self.data.get('status', 'unknown')})"

    def __repr__(self) -> str:
        """Zwraca reprezentację workspace'u"""
        return self.__str__()
