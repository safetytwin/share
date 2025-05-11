# Przewodnik testowania AI Environment Manager

Ten dokument zawiera szczegółowe instrukcje dotyczące testowania systemu AI Environment Manager. Zawiera scenariusze testowe, narzędzia i metodologię testowania dla deweloperów i testerów.

## Przygotowanie środowiska testowego

### Wymagania

- Python 3.8 lub nowszy
- pytest, pytest-cov, pytest-mock
- libvirt/KVM (do testowania modułu VM)
- Docker/Podman (do testowania modułu Container)
- Maszyna z co najmniej 8GB RAM i 4 rdzeniami CPU

### Instalacja zależności testowych

```bash
# Z katalogu głównego projektu
pip install -e ".[test]"

# Lub ręcznie
pip install pytest pytest-cov pytest-mock requests-mock coverage
```

### Konfiguracja środowiska testowego

```bash
# Utwórz folder na dane testowe
mkdir -p tests/data

# Konfiguracja testowa
export AI_ENV_TEST_MODE=1
export AI_ENV_CONFIG_DIR="./tests/data/config"
```

## Struktura testów

```
tests/
├── unit/                # Testy jednostkowe
│   ├── core/            # Testy modułu core
│   ├── p2p/             # Testy modułu p2p
│   ├── sharing/         # Testy modułu sharing
│   ├── runtime/         # Testy modułu runtime
│   ├── api/             # Testy modułu api
│   └── web/             # Testy modułu web
├── integration/         # Testy integracyjne
│   ├── networking/      # Testy komunikacji sieciowej
│   ├── storage/         # Testy warstwy danych
│   └── end_to_end/      # Testy end-to-end
├── performance/         # Testy wydajnościowe
├── fixtures/            # Dane testowe i fixtures
└── conftest.py          # Konfiguracja pytest
```

## Uruchamianie testów

### Testy jednostkowe

```bash
# Wszystkie testy jednostkowe
pytest tests/unit

# Konkretny moduł
pytest tests/unit/core

# Konkretny test
pytest tests/unit/core/test_workspace.py

# Z pomiarem pokrycia kodu
pytest tests/unit --cov=src
```

### Testy integracyjne

```bash
# Wszystkie testy integracyjne
pytest tests/integration

# Konkretna grupa
pytest tests/integration/networking

# Z pomiarem pokrycia kodu
pytest tests/integration --cov=src
```

### Testy wydajnościowe

```bash
# Uruchom testy wydajnościowe
pytest tests/performance
```

## Scenariusze testowe

### 1. Testy jednostkowe modułu Core

#### 1.1 Testy klasy Workspace

Testy sprawdzające funkcjonalność klasy Workspace z modułu core.

```python
# tests/unit/core/test_workspace.py

import pytest
from src.core.workspace import Workspace
from pathlib import Path

@pytest.fixture
def temp_workspace_dir(tmp_path):
    """Fixture tworzący tymczasowy katalog workspace'u"""
    return tmp_path / "workspaces" / "test-workspace"

def test_workspace_creation(temp_workspace_dir):
    """Test tworzenia nowego workspace'u"""
    # Przygotowanie
    workspace_name = "test-workspace"
    
    # Wykonanie
    workspace = Workspace(workspace_name, path=temp_workspace_dir, create_if_missing=True)
    
    # Weryfikacja
    assert workspace.name == workspace_name
    assert workspace.path == temp_workspace_dir
    assert workspace.config_path.exists()
    assert "name" in workspace.data
    assert workspace.data["name"] == workspace_name

def test_workspace_save_and_load(temp_workspace_dir):
    """Test zapisywania i wczytywania workspace'u"""
    # Przygotowanie
    workspace_name = "test-workspace"
    
    # Wykonanie - zapis
    workspace1 = Workspace(workspace_name, path=temp_workspace_dir, create_if_missing=True)
    workspace1.data["description"] = "Test description"
    workspace1.save()
    
    # Wykonanie - wczytywanie
    workspace2 = Workspace(workspace_name, path=temp_workspace_dir, create_if_missing=False)
    
    # Weryfikacja
    assert workspace2.data["description"] == "Test description"

def test_workspace_add_project(temp_workspace_dir):
    """Test dodawania projektu do workspace'u"""
    # Przygotowanie
    workspace = Workspace("test-workspace", path=temp_workspace_dir, create_if_missing=True)
    project_data = {
        "name": "test-project",
        "description": "Test project"
    }
    
    # Wykonanie
    result = workspace.add_project("test-project", project_data)
    
    # Weryfikacja
    assert result is True
    assert "test-project" in workspace.data["projects"]
    assert (temp_workspace_dir / "projects" / "test-project.yaml").exists()
    
    # Sprawdź czy można wczytać projekt
    project = workspace.get_project("test-project")
    assert project is not None
    assert project["name"] == "test-project"
    assert project["description"] == "Test project"

def test_workspace_export_import(temp_workspace_dir, tmp_path):
    """Test eksportowania i importowania workspace'u"""
    # Przygotowanie
    workspace1 = Workspace("test-workspace", path=temp_workspace_dir, create_if_missing=True)
    workspace1.data["description"] = "Test workspace for export"
    workspace1.save()
    
    # Dodaj projekt
    workspace1.add_project("test-project", {
        "name": "test-project",
        "description": "Test project"
    })
    
    export_path = tmp_path / "export" / "test-workspace.zip"
    
    # Wykonanie - eksport
    export_result = workspace1.export(export_path)
    
    # Weryfikacja eksportu
    assert export_result is not None
    assert export_result.exists()
    
    # Wykonanie - import
    import_result = Workspace.import_from_file(export_path, "imported-workspace")
    
    # Weryfikacja importu
    assert import_result is not None
    assert import_result.name == "imported-workspace"
    assert import_result.data["description"] == "Test workspace for export"
    assert "test-project" in import_result.data["projects"]
    
    # Sprawdź czy projekt został zaimportowany
    project = import_result.get_project("test-project")
    assert project is not None
    assert project["description"] == "Test project"
```

#### 1.2 Testy konfiguracji

Testy dla modułu config z modułu core.

```python
# tests/unit/core/test_config.py

import pytest
import os
import yaml
from src.core.config import Config

@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture tworzący tymczasowy plik konfiguracyjny"""
    config_file = tmp_path / "config.yaml"
    return config_file

def test_config_default_values(temp_config_file):
    """Test domyślnych wartości konfiguracji"""
    # Wykonanie
    config = Config(config_file=temp_config_file)
    
    # Weryfikacja
    assert "version" in config.config
    assert "paths" in config.config
    assert "workspaces" in config.config["paths"]

def test_config_save_and_load(temp_config_file):
    """Test zapisywania i wczytywania konfiguracji"""
    # Przygotowanie
    config1 = Config(config_file=temp_config_file)
    config1.config["test_key"] = "test_value"
    
    # Wykonanie - zapis
    config1.save()
    
    # Wykonanie - wczytywanie
    config2 = Config(config_file=temp_config_file)
    
    # Weryfikacja
    assert "test_key" in config2.config
    assert config2.config["test_key"] == "test_value"

def test_config_get_set(temp_config_file):
    """Test metod get i set"""
    # Przygotowanie
    config = Config(config_file=temp_config_file)
    
    # Wykonanie
    config.set("database.host", "localhost")
    config.set("database.port", 5432)
    
    # Weryfikacja
    assert config.get("database.host") == "localhost"
    assert config.get("database.port") == 5432
    
    # Test domyślnej wartości
    assert config.get("nonexistent.key", "default") == "default"

def test_config_deep_merge(temp_config_file):
    """Test głębokiego łączenia konfiguracji"""
    # Przygotowanie
    config = Config(config_file=temp_config_file)
    
    # Wykonanie
    config.set("nested.level1.level2", "original")
    config.save()
    
    # Zapisz alternatywną konfigurację do pliku
    with open(temp_config_file, 'w') as f:
        yaml.dump({
            "nested": {
                "level1": {
                    "level2": "updated",
                    "new_key": "new_value"
                }
            }
        }, f)
    
    # Wczytaj ponownie
    config2 = Config(config_file=temp_config_file)
    
    # Weryfikacja
    assert config2.get("nested.level1.level2") == "updated"
    assert config2.get("nested.level1.new_key") == "new_value"
```

### 2. Testy jednostkowe modułu P2P Discovery

```python
# tests/unit/p2p/test_discovery.py

import pytest
import json
import zlib
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from src.p2p.discovery import P2PDiscovery, PeerInfo

@pytest.fixture
def mock_socket():
    """Fixture tworzący mocka dla socketa"""
    with patch('socket.socket') as mock:
        # Przygotuj dane odpowiedzi
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        
        # Symuluj adres IP
        mock_instance.getsockname.return_value = ('192.168.1.100', 12345)
        
        yield mock

def test_p2p_discovery_initialization():
    """Test inicjalizacji modułu P2P Discovery"""
    # Wykonanie
    discovery = P2PDiscovery()
    
    # Weryfikacja
    assert discovery.port == 37777  # domyślny port
    assert discovery.peer_id is not None
    assert "peer_id" in discovery.node_info
    assert "hostname" in discovery.node_info
    assert "features" in discovery.node_info

@patch('src.p2p.discovery.socket.socket')
def test_p2p_discovery_start_stop(mock_socket):
    """Test uruchamiania i zatrzymywania odkrywania P2P"""
    # Przygotowanie
    discovery = P2PDiscovery()
    
    # Wykonanie - start
    result_start = discovery.start()
    
    # Weryfikacja - start
    assert result_start is True
    assert discovery.running is True
    assert discovery.listen_thread is not None
    assert discovery.broadcast_thread is not None
    
    # Wykonanie - stop
    result_stop = discovery.stop()
    
    # Weryfikacja - stop
    assert result_stop is True
    assert discovery.running is False

def test_peer_info_creation_and_update():
    """Test tworzenia i aktualizacji informacji o węźle"""
    # Przygotowanie
    peer_id = "test-peer-id"
    hostname = "test-host"
    ip = "192.168.1.200"
    timestamp = "2023-01-01T12:00:00"
    
    # Wykonanie - tworzenie
    peer_info = PeerInfo(peer_id, hostname, ip, timestamp)
    
    # Weryfikacja - tworzenie
    assert peer_info.peer_id == peer_id
    assert peer_info.hostname == hostname
    assert peer_info.ip == ip
    assert peer_info.timestamp == timestamp
    assert peer_info.status == "active"
    
    # Wykonanie - aktualizacja
    update_data = {
        "hostname": "updated-host",
        "environments": [{"name": "test-env"}],
        "version": "2.0.0"
    }
    peer_info.update(update_data)
    
    # Weryfikacja - aktualizacja
    assert peer_info.hostname == "updated-host"
    assert len(peer_info.environments) == 1
    assert peer_info.version == "2.0.0"

@patch('src.p2p.discovery.socket.socket')
def test_broadcast_and_receive(mock_socket):
    """Test wysyłania i odbierania rozgłoszeń"""
    # Przygotowanie
    discovery = P2PDiscovery()
    mock_callback = MagicMock()
    discovery.register_callback(mock_callback)
    
    # Symuluj odbiór danych
    def mock_recvfrom(size):
        # Utwórz dane testowe
        peer_data = {
            "peer_id": "remote-peer-id",
            "hostname": "remote-host",
            "ip": "192.168.1.200",
            "timestamp": "2023-01-01T12:00:00",
            "environments": [{"name": "remote-env"}]
        }
        
        # Skompresuj dane
        compressed_data = zlib.compress(json.dumps(peer_data).encode('utf-8'))
        return compressed_data, ('192.168.1.200', 37777)
    
    # Ustawienie mocka dla recvfrom
    mock_instance = mock_socket.return_value
    mock_instance.recvfrom.side_effect = [mock_recvfrom(4096), socket.timeout()]
    
    # Wykonanie
    discovery.running = True
    discovery._listen_for_peers()
    
    # Weryfikacja
    assert "remote-peer-id" in discovery.peers
    assert discovery.peers["remote-peer-id"].hostname == "remote-host"
    assert mock_callback.called
```

### 3. Testy integracyjne

#### 3.1 Testy integracji Core i P2P

```python
# tests/integration/test_core_p2p_integration.py

import pytest
import threading
import time
from src.core.workspace import Workspace
from src.p2p.discovery import discovery
from src.sharing.repository import repository

@pytest.fixture
def setup_environment(tmp_path):
    """Fixture konfigurujący środowisko testowe"""
    # Utwórz katalogi
    workspaces_dir = tmp_path / "workspaces"
    workspaces_dir.mkdir()
    
    # Konfiguracja dla testów
    config = {
        "paths": {
            "workspaces": str(workspaces_dir)
        }
    }
    
    # Nadpisz konfigurację (mock)
    with patch("src.core.config.config", config):
        yield workspaces_dir

def test_workspace_sharing_and_discovery(setup_environment):
    """Test integracji między workspace'ami a odkrywaniem P2P"""
    # Przygotowanie
    workspace = Workspace("test-workspace", 
                          path=setup_environment / "test-workspace", 
                          create_if_missing=True)
    workspace.data["description"] = "Test workspace for sharing"
    workspace.save()
    
    # Uruchom odkrywanie P2P
    discovery.start()
    
    # Udostępnij workspace
    repository.share_workspace("test-workspace", True)
    
    # Poczekaj na rozgłoszenie
    time.sleep(1)
    
    # Weryfikacja
    node_envs = discovery.node_info["environments"]
    
    assert len(node_envs) > 0
    assert any(env["name"] == "test-workspace" for env in node_envs)
    
    # Zatrzymaj odkrywanie
    discovery.stop()

def test_environment_update_propagation(setup_environment):
    """Test propagacji aktualizacji środowiska do odkrywania P2P"""
    # Przygotowanie
    workspace = Workspace("test-workspace2", 
                          path=setup_environment / "test-workspace2", 
                          create_if_missing=True)
    
    # Udostępnij workspace
    repository.share_workspace("test-workspace2", True)
    
    # Uruchom odkrywanie P2P
    discovery.start()
    
    # Aktualizuj workspace
    workspace.data["description"] = "Updated description"
    workspace.save()
    
    # Aktualizuj informacje o udostępnionych środowiskach
    repository.update_shared_workspace("test-workspace2")
    
    # Poczekaj na rozgłoszenie
    time.sleep(1)
    
    # Weryfikacja
    node_envs = discovery.node_info["environments"]
    
    assert len(node_envs) > 0
    matching_env = next((env for env in node_envs if env["name"] == "test-workspace2"), None)
    assert matching_env is not None
    assert matching_env["description"] == "Updated description"
    
    # Zatrzymaj odkrywanie
    discovery.stop()
```

#### 3.2 Testy integracji API i Core

```python
# tests/integration/test_api_core_integration.py

import pytest
import json
import threading
import time
from src.api.server import APIServer
from src.core.workspace import Workspace

@pytest.fixture
def setup_api_server(tmp_path):
    """Fixture konfigurujący serwer API i środowisko testowe"""
    # Utwórz katalogi
    workspaces_dir = tmp_path / "workspaces"
    workspaces_dir.mkdir()
    
    # Konfiguracja dla testów
    config = {
        "paths": {
            "workspaces": str(workspaces_dir)
        },
        "api": {
            "port": 37999  # Niestandardowy port dla testów
        }
    }
    
    # Nadpisz konfigurację (mock)
    with patch("src.core.config.config", config):
        # Utwórz i uruchom serwer API
        server = APIServer()
        server.start()
        
        # Poczekaj na uruchomienie serwera
        time.sleep(1)
        
        yield server, workspaces_dir
        
        # Zatrzymaj serwer API
        server.stop()

def test_api_create_workspace(setup_api_server):
    """Test tworzenia workspace'u przez API"""
    server, workspaces_dir = setup_api_server
    
    # Wykonanie - wywołanie API
    response = requests.post(
        f"http://localhost:{server.port}/workspaces",
        json={"name": "api-test", "description": "Created via API"}
    )
    
    # Weryfikacja odpowiedzi API
    assert response.status_code == 201
    data = response.json()
    assert data["workspace"]["name"] == "api-test"
    assert data["workspace"]["description"] == "Created via API"
    
    # Weryfikacja utworzenia plików
    workspace_dir = workspaces_dir / "api-test"
    assert workspace_dir.exists()
    assert (workspace_dir / "workspace.yaml").exists()

def test_api_add_project_to_workspace(setup_api_server):
    """Test dodawania projektu do workspace'u przez API"""
    server, workspaces_dir = setup_api_server
    
    # Najpierw utwórz workspace
    workspace = Workspace("api-project-test", 
                          path=workspaces_dir / "api-project-test", 
                          create_if_missing=True)
    workspace.save()
    
    # Wykonanie - wywołanie API
    response = requests.post(
        f"http://localhost:{server.port}/workspaces/api-project-test/projects",
        json={
            "name": "test-project",
            "description": "Project created via API",
            "languages": ["python"]
        }
    )
    
    # Weryfikacja odpowiedzi API
    assert response.status_code == 201
    data = response.json()
    assert data["project"]["name"] == "test-project"
    assert data["project"]["description"] == "Project created via API"
    
    # Weryfikacja utworzenia plików
    project_file = workspaces_dir / "api-project-test" / "projects" / "test-project.yaml"
    assert project_file.exists()
    
    # Weryfikacja aktualizacji workspace'u
    workspace_data = Workspace("api-project-test", path=workspaces_dir / "api-project-test").data
    assert "test-project" in workspace_data["projects"]
```

### 4. Testy wydajnościowe

```python
# tests/performance/test_workspace_operations.py

import pytest
import time
import random
import string
from src.core.workspace import Workspace

def random_string(length=10):
    """Generuje losowy ciąg znaków"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

@pytest.mark.performance
def test_workspace_creation_performance(tmp_path):
    """Test wydajności tworzenia workspace'ów"""
    # Liczba workspace'ów do utworzenia
    n_workspaces = 100
    
    # Przygotowanie
    workspace_path = tmp_path / "workspaces"
    workspace_path.mkdir()
    
    # Mierz czas
    start_time = time.time()
    
    # Utwórz n workspace'ów
    for i in range(n_workspaces):
        name = f"ws-{i}"
        workspace = Workspace(name, path=workspace_path / name, create_if_missing=True)
        workspace.save()
    
    # Oblicz czas wykonania
    duration = time.time() - start_time
    
    # Oczekiwania wydajnościowe - mniej niż 10ms na workspace
    assert duration < n_workspaces * 0.01
    
    print(f"Czas tworzenia {n_workspaces} workspace'ów: {duration:.2f}s ({duration/n_workspaces*1000:.2f}ms/workspace)")

@pytest.mark.performance
def test_workspace_export_import_performance(tmp_path):
    """Test wydajności eksportu i importu workspace'u z projektami"""
    # Przygotowanie
    workspace_path = tmp_path / "workspaces" / "perf-test"
    workspace_path.mkdir(parents=True)
    
    # Utwórz workspace z wieloma projektami
    workspace = Workspace("perf-test", path=workspace_path, create_if_missing=True)
    
    # Utwórz 50 projektów
    for i in range(50):
        project_data = {
            "name": f"project-{i}",
            "description": f"Performance test project {i}",
            "content": random_string(1000)  # Dodaj trochę danych
        }
        workspace.add_project(f"project-{i}", project_data)
    
    export_path = tmp_path / "exports" / "perf-test.zip"
    export_path.parent.mkdir(parents=True)
    
    # Zmierz czas eksportu
    export_start = time.time()
    export_result = workspace.export(export_path)
    export_duration = time.time() - export_start
    
    # Zmierz czas importu
    import_start = time.time()
    import_result = Workspace.import_from_file(export_path, "perf-test-imported")
    import_duration = time.time() - import_start
    
    # Oczekiwania wydajnościowe
    assert export_duration < 2.0  # Mniej niż 2 sekundy na eksport
    assert import_duration < 2.0  # Mniej niż 2 sekundy na import
    
    print(f"Czas eksportu workspace'u z 50 projektami: {export_duration:.2f}s")
    print(f"Czas importu workspace'u z 50 projektami: {import_duration:.2f}s")
```

## Narzędzia do testowania

### Mocking

Używanie pytest-mock do izolacji komponentów:

```python
def test_with_mock(mocker):
    # Mockuj zewnętrzną zależność
    mock_function = mocker.patch('src.module.external_function')
    mock_function.return_value = "mocked_value"
    
    # Wywołaj testowaną funkcję
    result = your_function()
    
    # Sprawdź czy mock został wywołany
    mock_function.assert_called_once()
    
    # Sprawdź wynik
    assert result == "expected_value"
```

### Fixtures sieciowe

Tworzenie mocków dla socketów i komunikacji sieciowej:

```python
@pytest.fixture
def mock_network_environment():
    """Fixture tworzący symulowane środowisko sieciowe"""
    # Przygotuj mockowane sockety i połączenia
    with patch('socket.socket') as mock_socket, \
         patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Konfiguracja mocków
        mock_socket_instance = MagicMock()
        mock_socket.return_value = mock_socket_instance
        
        # Odpowiedź HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            'socket': mock_socket_instance,
            'get': mock_get,
            'post': mock_post
        }
```

### Logowanie i raportowanie

Aby generować raport z testów:

```bash
# Raport HTML z pokryciem kodu
pytest --cov=src --cov-report=html

# Raport JUnit XML (dla CI/CD)
pytest --junitxml=results.xml
```

## Automatyzacja testów

Przykładowy skrypt CI/CD dla GitHub Actions:

```yaml
name: Run Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[test]"
    - name: Run unit tests
      run: |
        pytest tests/unit --cov=src --cov-report=xml
    - name: Run integration tests
      run: |
        pytest tests/integration
    - name: Upload coverage report
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

## Wskazówki dla testerów

1. **Izolacja testów** - każdy test powinien być niezależny od innych
2. **Przygotowywanie danych testowych** - używaj fixtures do przygotowania danych
3. **Testowanie warunków brzegowych** - uwzględnij scenariusze błędów i wyjątków
4. **Szybkość wykonania** - testy powinny być szybkie; wydziel wolniejsze testy do osobnych grup
5. **Czystość** - testy powinny po sobie sprzątać, nie pozostawiając śladów
6. **Czytelność** - używaj jasnych nazw testów i komentarzy wyjaśniających cel testu
# Przewodnik testowania AI Environment Manager

Ten dokument zawiera szczegółowe instrukcje dotyczące testowania systemu AI Environment Manager. Zawiera scenariusze testowe, narzędzia i metodologię testowania dla deweloperów i testerów.

## Przygotowanie środowiska testowego

### Wymagania

- Python 3.8 lub nowszy
- pytest, pytest-cov, pytest-mock
- libvirt/KVM (do testowania modułu VM)
- Docker/Podman (do testowania modułu Container)
- Maszyna z co najmniej 8GB RAM i 4 rdzeniami CPU

### Instalacja zależności testowych

```bash
# Z katalogu głównego projektu
pip install -e ".[test]"

# Lub ręcznie
pip install pytest pytest-cov pytest-mock requests-mock coverage
```

### Konfiguracja środowiska testowego

```bash
# Utwórz folder na dane testowe
mkdir -p tests/data

# Konfiguracja testowa
export AI_ENV_TEST_MODE=1
export AI_ENV_CONFIG_DIR="./tests/data/config"
```

## Struktura testów

```
tests/
├── unit/                # Testy jednostkowe
│   ├── core/            # Testy modułu core
│   ├── p2p/             # Testy modułu p2p
│   ├── sharing/         # Testy modułu sharing
│   ├── runtime/         # Testy modułu runtime
│   ├── api/             # Testy modułu api
│   └── web/             # Testy modułu web
├── integration/         # Testy integracyjne
│   ├── networking/      # Testy komunikacji sieciowej
│   ├── storage/         # Testy warstwy danych
│   └── end_to_end/      # Testy end-to-end
├── performance/         # Testy wydajnościowe
├── fixtures/            # Dane testowe i fixtures
└── conftest.py          # Konfiguracja pytest
```

## Uruchamianie testów

### Testy jednostkowe

```bash
# Wszystkie testy jednostkowe
pytest tests/unit

# Konkretny moduł
pytest tests/unit/core

# Konkretny test
pytest tests/unit/core/test_workspace.py

# Z pomiarem pokrycia kodu
pytest tests/unit --cov=src
```

### Testy integracyjne

```bash
# Wszystkie testy integracyjne
pytest tests/integration

# Konkretna grupa
pytest tests/integration/networking

# Z pomiarem pokrycia kodu
pytest tests/integration --cov=src
```

### Testy wydajnościowe

```bash
# Uruchom testy wydajnościowe
pytest tests/performance
```

## Scenariusze testowe

