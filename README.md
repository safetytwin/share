# share
# Podsumowanie projektu AI Environment Manager

kompleksowe rozwiązanie do zarządzania, udostępniania i klonowania środowisk AI w sieci lokalnej. Poniżej przedstawiam kluczowe dokumenty i wytyczne dla dalszego rozwoju projektu.

## Główne dokumenty

1. **Architektura systemu** - Szczegółowa architektura systemu, opis komponentów i ich interakcji
2. **Podręcznik użytkownika** - Kompletna instrukcja obsługi dla użytkowników końcowych
3. **Przewodnik testowania** - Metodologia i scenariusze testowe dla deweloperów
4. **Instalacja i konfiguracja** - Szczegółowe instrukcje instalacji i konfiguracji na różnych platformach
5. **Prompty dla dalszego rozwoju** - Gotowe prompty do generowania kolejnych modułów systemu
6. **[REST API Guide](docs/rest_api_guide.md)** - Kompletna dokumentacja REST API

## Kluczowe moduły zaimplementowane

1. **P2P Discovery** - Moduł automatycznego wykrywania węzłów w sieci lokalnej
2. **Core Workspace** - Podstawowy model danych dla workspace'ów, projektów i środowisk
3. **REST API Server** - Pełne REST API do zarządzania systemem, VM i P2P
4. **REST API Client** - Biblioteka kliencka do integracji z API

## Unikalne cechy rozwiązania

1. **Architektura P2P** - System działa w modelu peer-to-peer bez centralnego serwera
2. **Federacja węzłów** - Możliwość rozproszenia obciążeń między wieloma maszynami
3. **Wieloplatformowość** - Wsparcie dla różnych systemów operacyjnych i środowisk wykonawczych
4. **One-Click Deployment** - Możliwość sklonowania środowiska jednym kliknięciem
5. **Automatyczna adaptacja** - Dostosowanie do dostępnych zasobów sprzętowych
6. **REST API** - Pełne REST API do integracji z zewnętrznymi systemami

## Instalacja

### Automatyczna instalacja

Użyj skryptu instalacyjnego, który zainstaluje wszystkie wymagane zależności i skonfiguruje usługi:

```bash
# Pełna instalacja
./install.sh

# Instalacja z pominięciem zależności systemowych
./install.sh --skip-system-deps

# Instalacja z pominięciem usługi systemowej
./install.sh --skip-service-install

# Instalacja w trybie nieinteraktywnym
./install.sh --non-interactive
```

### Ręczna instalacja

1. Zainstaluj wymagane zależności systemowe:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv libvirt-dev pkg-config \
    libvirt-daemon libvirt-daemon-system qemu-kvm bridge-utils virtinst \
    libvirt-clients build-essential python3-dev

# Fedora/CentOS/RHEL
sudo dnf update -y
sudo dnf install -y python3 python3-pip python3-virtualenv libvirt-devel \
    pkgconfig libvirt libvirt-daemon-kvm qemu-kvm bridge-utils \
    virt-install libvirt-client gcc python3-devel
```

2. Utwórz i aktywuj wirtualne środowisko Python:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Zainstaluj zależności Pythona:

```bash
pip install -e .
```

## Uruchomienie REST API

### Jako usługa systemowa

1. Zainstaluj usługę:

```bash
# Utwórz katalogi dla logów i PID
sudo mkdir -p /var/log/safetytwin /var/run/safetytwin

# Skopiuj plik usługi
sudo cp scripts/safetytwin-rest-api.service /etc/systemd/system/

# Załaduj konfigurację systemd
sudo systemctl daemon-reload

# Włącz usługę do autostartu
sudo systemctl enable safetytwin-rest-api

# Uruchom usługę
sudo systemctl start safetytwin-rest-api

# Sprawdź status
sudo systemctl status safetytwin-rest-api
```

### Ręczne uruchomienie

```bash
# Uruchom w trybie foreground
python scripts/start_rest_api.py start --foreground

# Uruchom jako daemon
python scripts/start_rest_api.py start

# Sprawdź status
python scripts/start_rest_api.py status

# Zatrzymaj
python scripts/start_rest_api.py stop
```

## Przykłady użycia REST API

Zobacz [przykłady użycia REST API](examples/rest_api_usage.py) oraz [dokumentację REST API](docs/rest_api_guide.md).

## Kolejne kroki

1. **Implementacja modułów wykonawczych** (Runtime) - Użyj promptu dla modułów VM, Container i Process
2. **Rozwój interfejsu webowego** - Stwórz nowoczesny UI w React z komunikacją przez WebSocket
3. **Implementacja modułu Repository i Transfer** - Dokończ implementację mechanizmów udostępniania
4. **Testy** - Stwórz komplet testów jednostkowych i integracyjnych
5. **Dokumentacja użytkownika** - Uzupełnij dokumentację o więcej przykładów i przypadków użycia

To rozwiązanie, inspirowane systemami takimi jak LocalAI z funkcjami P2P, Codezero i integracja Conda z JuiceFS, zapewnia bezproblemowe zarządzanie środowiskami AI w zespołach deweloperskich, pozwalając na natychmiastowe rozpoczęcie pracy bez skomplikowanej konfiguracji środowiska.

# Specyfikacja funkcjonalna: AI Environment Manager

## 1. Cel systemu

Stworzenie rozwiązania umożliwiającego proste udostępnianie i klonowanie gotowych środowisk programistycznych dla projektów AI między komputerami w sieci lokalnej. System zapewnia natychmiastowy dostęp do skonfigurowanych narzędzi i projektów bez konieczności ręcznej konfiguracji.

## 2. Główne funkcjonalności

### 2.1. Automatyczne wykrywanie i udostępnianie

- Automatyczne wykrywanie hostów w sieci lokalnej udostępniających środowiska AI
- Rozgłaszanie dostępnych środowisk w sieci lokalnej (zero-configuration networking)
- Przeglądanie dostępnych środowisk z poziomu interfejsu przeglądarki
- Filtrowanie i wyszukiwanie środowisk według typów, narzędzi i języków

### 2.2. Zarządzanie środowiskami

- Tworzenie, edycja i usuwanie workspace'ów z projektami AI
- Włączanie/wyłączanie udostępniania workspace'ów dla innych użytkowników
- Eksportowanie i importowanie workspace'ów
- Automatyczne przydzielanie zasobów (CPU, RAM, dysk) dla środowisk

### 2.3. Klonowanie środowisk

- Jednym kliknięciem pobranie wybranego środowiska z innego komputera w sieci
- Automatyczna konfiguracja pobranego środowiska
- Adaptacja środowiska do zasobów lokalnego komputera
- Automatyczne uruchamianie środowiska po pobraniu

### 2.4. Dostęp do środowisk

- Dostęp przez przeglądarkę do wszystkich narzędzi w środowisku
- Automatyczne logowanie do narzędzi (VSCode, JupyterLab, Le Chat)
- Zintegrowany terminal dostępny z poziomu interfejsu www
- Automatyczne uruchamianie środowisk przy starcie systemu

### 2.5. Integracja z projektami

- Automatyczne klonowanie repozytoriów git podczas pobierania środowiska
- Automatyczna konfiguracja środowiska na podstawie plików konfiguracyjnych projektu
- Synchronizacja zmian między projektami w różnych workspace'ach
- Integracja z narzędziami CI/CD

## 3. Komponenty systemu

### 3.1. Moduł wykrywania (Discovery)

- Protokół rozgłaszania dostępnych środowisk w sieci lokalnej
- Mechanizm automatycznego wykrywania hostów w sieci
- Protokół pobierania metadanych o dostępnych środowiskach
- Wykrywanie dostępnych zasobów na komputerze

### 3.2. Moduł udostępniania (Sharing)

- Serwer HTTP do udostępniania plików
- Kompresja i szyfrowanie przesyłanych danych
- Mechanizm autoryzacji dostępu do środowisk
- System kolejkowania równoczesnych transferów

### 3.3. Moduł zarządzania (Management)

- Tworzenie i konfiguracja workspace'ów
- Zarządzanie projektami w workspace'ach
- Zarządzanie środowiskami (VM, kontenery, procesy lokalne)
- System przydzielania zasobów sprzętowych

### 3.4. Interfejs webowy (Web UI)

- Panel dostępny przez przeglądarkę
- Intuicyjny interfejs one-click-deployment
- Dashboard z przeglądem środowisk
- Zarządzanie procesem pobierania i udostępniania

## 4. Wymagania techniczne

### 4.1. Wymagania sprzętowe (minimum)

- CPU: 2 rdzenie
- RAM: 4 GB
- Dysk: 20 GB wolnego miejsca
- Sieć: Dostęp do sieci lokalnej

### 4.2. Wymagania sprzętowe (zalecane)

- CPU: 8+ rdzeni
- RAM: 16+ GB
- Dysk: 100+ GB wolnego miejsca (najlepiej SSD)
- Sieć: Gigabit Ethernet

### 4.3. Wymagania programowe

- Python 3.8+
- Zależności systemowe: libvirt/QEMU, Docker/Podman (opcjonalnie)
- Przeglądarka internetowa: Chrome, Firefox, Edge (najnowsze wersje)

## 5. Interakcje użytkownika

### 5.1. Udostępnianie środowiska

1. Użytkownik uruchamia aplikację na swoim komputerze
2. Wybiera workspace do udostępnienia
3. Klika przycisk "Udostępnij"
4. System automatycznie rozgłasza dostępność środowiska w sieci

### 5.2. Pobieranie środowiska

1. Użytkownik uruchamia aplikację na swoim komputerze
2. Przegląda listę dostępnych środowisk w sieci
3. Wybiera interesujące go środowisko
4. Klika przycisk "Pobierz"
5. System automatycznie pobiera, konfiguruje i uruchamia środowisko

### 5.3. Uruchamianie środowiska

1. Użytkownik wybiera pobrany workspace
2. Klika przycisk "Uruchom"
3. System uruchamia wszystkie komponenty środowiska
4. Użytkownik otrzymuje linki do dostępu przez przeglądarkę

## 6. Protokoły i formaty danych

### 6.1. Protokół wykrywania

- Multicast UDP na porcie 37777
- Format danych: Skompresowany JSON z informacjami o hoście i dostępnych środowiskach
- Interwał rozgłaszania: 10 sekund

### 6.2. Protokół udostępniania

- HTTP/REST API na porcie 37778
- Format danych: JSON dla metadanych, ZIP dla transferu środowisk
- Autoryzacja: Podstawowa autoryzacja nagłówków HTTP

### 6.3. Format workspace'u

- Katalog z plikami YAML zawierającymi konfigurację
- Podkatalogi dla projektów, środowisk i danych
- Wersjonowanie konfiguracji
- Skrypty inicjalizacyjne dla różnych platform

## 7. Bezpieczeństwo

- Ograniczenie udostępniania tylko do sieci lokalnej
- Opcjonalne szyfrowanie transferów
- Walidacja integralności pobranych danych
- Sandbox dla uruchamianych środowisk

## 8. Rozszerzalność

- Plugin API dla dodawania nowych typów środowisk
- Wsparcie dla skryptów niestandardowych
- Możliwość dodawania własnych szablonów środowisk
- Integracja z dodatkowymi narzędziami AI
