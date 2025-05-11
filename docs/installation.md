
# Instalacja i konfiguracja AI Environment Manager

Ten dokument zawiera szczegółowe instrukcje dotyczące instalacji i konfiguracji systemu AI Environment Manager na różnych platformach.

## Wymagania systemowe

### Minimalne wymagania

- **CPU**: 2 rdzenie
- **RAM**: 4 GB
- **Dysk**: 20 GB wolnej przestrzeni
- **System operacyjny**: Linux (Ubuntu 20.04+, Debian 11+), macOS 12+, Windows 10/11
- **Python**: 3.8 lub nowszy

### Zalecane wymagania

- **CPU**: 8+ rdzeni
- **RAM**: 16+ GB
- **Dysk**: 100+ GB wolnej przestrzeni (SSD)
- **Sieć**: Gigabit Ethernet
- **System operacyjny**: Linux (Ubuntu 22.04+)
- **Python**: 3.10 lub nowszy

### Wymagania dodatkowe (opcjonalne)

- **Docker/Podman**: Do obsługi środowisk kontenerowych
- **libvirt/KVM**: Do obsługi maszyn wirtualnych
- **NVIDIA GPU + sterowniki CUDA**: Do środowisk AI z akceleracją GPU

## Instalacja

### Instalacja z PyPI

Najłatwiejszym sposobem instalacji AI Environment Manager jest użycie pip:

```bash
# Instalacja stabilnej wersji
pip install ai-environment-manager

# Instalacja najnowszej wersji deweloperskiej
pip install ai-environment-manager --pre
```

### Instalacja z repozytorium

Aby zainstalować najnowszą wersję z repozytorium:

```bash
# Klonowanie repozytorium
git clone https://github.com/ai-environment-manager/ai-environment-manager.git
cd ai-environment-manager

# Instalacja w trybie edycji (dla deweloperów)
pip install -e .

# Instalacja z dodatkowymi zależnościami
pip install -e ".[dev,test,docs]"
```

### Instalacja zależności systemowych

#### Linux (Ubuntu/Debian)

```bash
# Podstawowe zależności
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip

# Zależności dla maszyn wirtualnych
sudo apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils

# Zależności dla kontenerów
sudo apt-get install -y docker.io docker-compose

# Dodaj użytkownika do grup
sudo usermod -aG libvirt $USER
sudo usermod -aG docker $USER

# Sterowniki NVIDIA (opcjonalnie)
sudo apt-get install -y nvidia-driver-525 nvidia-container-toolkit
```

#### macOS

```bash
# Instalacja Homebrew (jeśli nie jest zainstalowany)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalacja zależności
brew install python
brew install --cask docker
```

#### Windows

1. Zainstaluj [Python](https://www.python.org/downloads/) (zalecana wersja 3.10+)
2. Zainstaluj [Docker Desktop](https://www.docker.com/products/docker-desktop)
3. Dla wsparcia maszyn wirtualnych:
   - Włącz funkcję Hyper-V w Windows
   - lub zainstaluj [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Inicjalizacja

Po zainstalowaniu AI Environment Manager, należy przeprowadzić inicjalizację:

```bash
# Inicjalizacja z domyślnymi ustawieniami
ai-env-manager init

# Inicjalizacja z interaktywną konfiguracją
ai-env-manager init --interactive

# Inicjalizacja z plikiem konfiguracyjnym
ai-env-manager init --config path/to/config.yaml
```

## Struktura katalogów

Domyślna struktura katalogów AI Environment Manager:

```
~/.ai-environment/
├── config.yaml             # Główny plik konfiguracyjny
├── workspaces/             # Katalog z workspace'ami
│   ├── workspace1/         # Przykładowy workspace
│   │   ├── workspace.yaml  # Konfiguracja workspace'u
│   │   ├── projects/       # Pliki konfiguracyjne projektów
│   │   ├── environments/   # Pliki konfiguracyjne środowisk
│   │   └── data/           # Dane projektów
├── templates/              # Szablony workspace'ów i środowisk
├── exports/                # Wyeksportowane workspace'y
├── vm-images/              # Obrazy bazowe dla maszyn wirtualnych
├── docker/                 # Pliki Dockerfile i docker-compose.yml
└── logs/                   # Pliki logów
```

## Konfiguracja

### Podstawowa konfiguracja

Główny plik konfiguracyjny znajduje się domyślnie w `~/.ai-environment/config.yaml`. Poniżej podstawowe ustawienia:

```yaml
# Podstawowa konfiguracja AI Environment Manager
version: "1.0.0"

# Ścieżki do katalogów
paths:
  workspaces: "~/.ai-environment/workspaces"
  templates: "~/.ai-environment/templates"
  exports: "~/.ai-environment/exports"
  vm_images: "~/.ai-environment/vm-images"
  docker: "~/.ai-environment/docker"
  logs: "~/.ai-environment/logs"

# Ustawienia użytkownika
user:
  name: "John Doe"
  email: "john.doe@example.com"

# Ustawienia API
api:
  port: 37780
  host: "127.0.0.1"
  allow_remote: false
  use_auth: false
  key: ""  # Klucz API (jeśli use_auth=true)

# Ustawienia interfejsu webowego
web:
  port: 8000
  open_browser: true
  theme: "light"  # light, dark, system

# Ustawienia wykrywania P2P
p2p:
  discovery:
    port: 37777
    broadcast_interval: 10  # sekundy
    enable: true
  node:
    name: ""  # Pozostaw puste dla automatycznego użycia hostname
    id: ""    # Pozostaw puste dla automatycznego generowania

# Ustawienia zasobów
resources:
  cpu_reservation: 2  # liczba rdzeni zarezerwowanych dla hosta
  memory_reservation_percent: 20  # procent pamięci zarezerwowany dla hosta
  disk_reservation_gb: 20  # GB zarezerwowane dla hosta

# Ustawienia środowisk wykonawczych
runtime:
  vm:
    enabled: true
    type: "kvm"  # kvm, virtualbox
    network: "default"
  container:
    enabled: true
    type: "docker"  # docker, podman
  process:
    enabled: true
```

### Zmiana ustawień

Ustawienia można zmieniać na kilka sposobów:

```bash
# Edycja pliku konfiguracyjnego
ai-env-manager config edit

# Zmiana pojedynczego ustawienia
ai-env-manager config set api.port 8080

# Zmiana wielu ustawień
ai-env-manager config set web.theme=dark p2p.discovery.enable=false

# Reset do domyślnych ustawień
ai-env-manager config reset
```

## Zmienne środowiskowe

AI Environment Manager obsługuje konfigurację przez zmienne środowiskowe, co jest przydatne w środowiskach CI/CD i kontenerach:

```bash
# Katalog konfiguracyjny
export AI_ENV_CONFIG_DIR="/path/to/config"

# Port API
export AI_ENV_API_PORT=37780

# Klucz API
export AI_ENV_API_KEY="your-api-key"

# Włączenie/wyłączenie wykrywania P2P
export AI_ENV_P2P_ENABLE=true

# Włączenie/wyłączenie uruchamiania automatycznego
export AI_ENV_AUTOSTART=false
```

## Konfiguracja dla specyficznych środowisk

### Konfiguracja libvirt/KVM

Aby w pełni korzystać z maszyn wirtualnych, należy odpowiednio skonfigurować libvirt:

```bash
# Utwórz domyślną sieć jeśli nie istnieje
sudo virsh net-define /etc/libvirt/qemu/networks/default.xml
sudo virsh net-start default
sudo virsh net-autostart default

# Sprawdź status sieci
sudo virsh net-list --all

# Konfiguracja uprawnień
sudo usermod -aG libvirt $USER
sudo usermod -aG kvm $USER
```

Aby umożliwić przekazanie GPU do maszyny wirtualnej:

```bash
# Utwórz plik konfiguracyjny dla IOMMU
cat << EOF | sudo tee /etc/modprobe.d/vfio.conf
options vfio-pci ids=10de:1c03,10de:10f1
EOF

# Dodaj moduły do INITRAMFS
echo "vfio vfio_iommu_type1 vfio_pci vfio_virqfd" | sudo tee -a /etc/modules

# Zaktualizuj INITRAMFS
sudo update-initramfs -u
```

### Konfiguracja Docker

Dla optymalnego działania środowisk kontenerowych:

```bash
# Upewnij się, że użytkownik jest w grupie docker
sudo usermod -aG docker $USER

# Konfiguracja Docker do obsługi GPU (dla NVIDIA)
cat << EOF | sudo tee /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF

# Restart Docker
sudo systemctl restart docker
```

## Uruchamianie jako usługa systemowa

### Linux (systemd)

Aby uruchomić AI Environment Manager jako usługę systemową:

```bash
# Utwórz plik usługi
cat << EOF | sudo tee /etc/systemd/system/ai-env-manager.service
[Unit]
Description=AI Environment Manager
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER
ExecStart=$(which ai-env-manager) daemon
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

# Włącz i uruchom usługę
sudo systemctl enable ai-env-manager
sudo systemctl start ai-env-manager

# Sprawdź status
sudo systemctl status ai-env-manager
```

### Windows

Dla Windows można użyć nssm (Non-Sucking Service Manager):

1. Pobierz [nssm](https://nssm.cc/download)
2. Otwórz wiersz poleceń jako administrator
3. Wykonaj:

```batch
nssm install AI-Environment-Manager "C:\Path\To\Python\python.exe" "-m ai_env_manager daemon"
nssm set AI-Environment-Manager DisplayName "AI Environment Manager"
nssm set AI-Environment-Manager Start SERVICE_AUTO_START
nssm start AI-Environment-Manager
```

## Konfiguracja zaawansowana

### Filtrowanie sieci dla P2P

Aby ograniczyć wykrywanie P2P tylko do określonych sieci:

```yaml
# W pliku config.yaml
p2p:
  discovery:
    networks:
      - "192.168.1.0/24"  # Tylko lokalna sieć
      - "10.0.0.0/8"      # Prywatna sieć firmowa
```

### Konfiguracja proxy

Jeśli działasz za firewallem lub proxy:

```yaml
# W pliku config.yaml
network:
  proxy:
    http: "http://proxy.example.com:8080"
    https: "http://proxy.example.com:8080"
    no_proxy: "localhost,127.0.0.1,192.168.1.0/24"
```

### Konfiguracja SSL/TLS dla API

Aby zabezpieczyć API przez HTTPS:

```yaml
# W pliku config.yaml
api:
  use_ssl: true
  ssl_cert: "/path/to/cert.pem"
  ssl_key: "/path/to/key.pem"
```

### Integracja z zewnętrznymi systemami

#### Integracja z GitLab/GitHub

```yaml
# W pliku config.yaml
integrations:
  git:
    provider: "github"  # github, gitlab, bitbucket
    token: "your-access-token"
    username: "your-username"
```

#### Integracja z systemami CI/CD

```yaml
# W pliku config.yaml
integrations:
  ci:
    provider: "jenkins"  # jenkins, github-actions, gitlab-ci
    url: "https://jenkins.example.com"
    token: "your-jenkins-token"
```

## Rozwiązywanie problemów

### Diagnostyka

```bash
# Sprawdź status usług
ai-env-manager status

# Wyświetl logi
ai-env-manager logs

# Sprawdź połączenia sieciowe
ai-env-manager network check

# Uruchom diagnostykę
ai-env-manager diagnostics
```

### Typowe problemy

#### Problem z uprawnieniami do Docker

**Objaw**: Błąd `Permission denied` przy próbie użycia Docker

**Rozwiązanie**:
```bash
sudo usermod -aG docker $USER
# Wyloguj się i zaloguj ponownie
```

#### Problem z wykrywaniem P2P

**Objaw**: Nie wykrywa innych hostów w sieci

**Rozwiązanie**:
```bash
# Sprawdź firewall
sudo ufw status
sudo ufw allow 37777/udp

# Sprawdź konfigurację sieci
ai-env-manager config set p2p.discovery.broadcast_interval 5
ai-env-manager restart
```

#### Problem z uruchamianiem maszyn wirtualnych

**Objaw**: Błąd przy próbie uruchomienia VM

**Rozwiązanie**:
```bash
# Sprawdź libvirt
sudo systemctl status libvirtd
sudo virsh list --all

# Sprawdź uprawnienia
sudo ls -la /var/run/libvirt/libvirt-sock
sudo usermod -aG libvirt $USER
```

## Aktualizacja

```bash
# Aktualizacja z PyPI
pip install --upgrade ai-environment-manager

# Aktualizacja z repozytorium
cd path/to/ai-environment-manager
git pull
pip install -e .

# Migracja danych
ai-env-manager migrate
```