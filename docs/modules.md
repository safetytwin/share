
share your twin
# Moduł P2P Discovery (`src/p2p/discovery.py`)

Ten moduł implementuje mechanizm automatycznego wykrywania węzłów w sieci lokalnej bazując na rozwiązaniach P2P.


## Kluczowe funkcje modułu:

1. **Automatyczne wykrywanie** - implementuje protokół P2P do wykrywania innych węzłów w sieci lokalnej
2. **Rozgłaszanie środowisk** - umożliwia rozgłaszanie dostępnych środowisk AI w sieci
3. **Callback API** - pozwala na rejestrację funkcji wywoływanych przy odkryciu nowego węzła
4. **Monitorowanie aktywności** - śledzi aktywność węzłów i oznacza nieaktywne
5. **Kompresja danych** - optymalizuje transfer danych przez kompresję

## Ulepszenia względem pierwszej wersji:

- Pełna abstrakcja w formie klasy `PeerInfo`
- System callbacków do powiadamiania o zmianach
- Mechanizm wykrywania obsługiwanych funkcji (np. VM, kontenery)
- Wsparcie dla federacji węzłów (z LocalAI)
- Optymalizacja danych przez kompresję (z zlib)
- Bardziej szczegółowe logowanie



# Moduł Core Workspace (`src/core/workspace.py`)

Ten moduł implementuje model workspace'u - podstawowej jednostki organizacyjnej dla środowisk AI.

```python

```

## Kluczowe funkcje klasy Workspace:

1. **Zarządzanie workspace'ami**:
   - Tworzenie nowych workspace'ów z domyślną konfiguracją
   - Wczytywanie istniejących workspace'ów
   - Zapisywanie zmian w konfiguracji

2. **Eksport i import**:
   - Eksportowanie workspace'u do pliku ZIP (z danymi lub bez)
   - Importowanie workspace'u z pliku ZIP
   - Automatyczne generowanie dokumentacji README

3. **Zarządzanie projektami i środowiskami**:
   - Dodawanie nowych projektów i środowisk
   - Usuwanie projektów i środowisk
   - Pobieranie informacji o projektach i środowiskach

4. **Zarządzanie stanem**:
   - Aktualizacja statusu workspace'u (running, stopped, paused, error)
   - Listowanie wszystkich dostępnych workspace'ów

## Ulepszenia względem pierwszej wersji:

- Pełna klasa z metodami do zarządzania wszystkimi aspektami workspace'u
- Obsługa eksportu i importu workspace'ów
- Automatyczne generowanie dokumentacji README
- Bezpieczne zarządzanie danymi podczas eksportu/importu
- Rozszerzone funkcje związane z projektami i środowiskami
- Rozbudowany system statusów
- Lepsze logowanie i obsługa błędów
# Moduł Core Workspace (`src/core/workspace.py`)

Ten moduł implementuje model workspace'u - podstawowej jednostki organizacyjnej dla środowisk AI.
































# Moduł Core Config (`src/core/config.py`)

Ten moduł implementuje zarządzanie konfiguracją systemu AI Environment Manager.


## Wyjaśnienie kluczowych elementów

### 1. Struktura konfiguracji

Klasa `Config` zarządza konfiguracją całego systemu, która jest przechowywana w hierarchicznej strukturze słowników. Umożliwia to łatwą organizację ustawień dotyczących różnych aspektów systemu, takich jak ścieżki, API, P2P, zasoby, itp.

### 2. Domyślna konfiguracja 

`DEFAULT_CONFIG` zawiera wszystkie domyślne wartości konfiguracyjne, co zapewnia spójne działanie systemu nawet bez pliku konfiguracyjnego. Jest to szczególnie ważne przy pierwszym uruchomieniu.

### 3. Zmienne środowiskowe

Moduł obsługuje konfigurację przez zmienne środowiskowe, co jest przydatne w środowiskach CI/CD i kontenerach. Wartości z zmiennych środowiskowych mają priorytet nad domyślnymi, ale mogą być nadpisane przez plik konfiguracyjny.

### 4. Metody dostępu

Metody `get` i `set` umożliwiają łatwy dostęp do zagnieżdżonych wartości konfiguracyjnych za pomocą składni z kropkami, np. `config.get("api.port")`.

### 5. Bezpieczeństwo

Metoda `_safe_config` tworzy kopię konfiguracji z ukrytymi wrażliwymi danymi (jak klucze API, tokeny), co jest ważne przy logowaniu i wyświetlaniu.

### 6. Zarządzanie katalogami

Funkcja `ensure_directories` tworzy wszystkie wymagane katalogi na podstawie konfiguracji, co upraszcza instalację i konfigurację.

### 7. Konfiguracja logowania

Funkcja `configure_logging` konfiguruje system logowania na podstawie ustawień, zapewniając elastyczność w zarządzaniu logami.

## Użycie modułu

```python
from src.core.config import config, ensure_directories

# Pobieranie wartości
api_port = config.get("api.port")  # domyślnie 37780

# Ustawianie wartości
config.set("web.theme", "dark")

# Resetowanie do wartości domyślnych
config.reset()

# Tworzenie katalogów
ensure_directories()
```

Ten moduł stanowi fundament całego systemu AI Environment Manager, zapewniając spójne zarządzanie konfiguracją we wszystkich pozostałych modułach.





# Moduł Runtime VM (`src/runtime/vm.py`)

Ten moduł implementuje zarządzanie maszynami wirtualnymi dla AI Environment Manager, korzystając z libvirt/KVM.

