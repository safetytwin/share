# Podręcznik użytkownika AI Environment Manager

## Wprowadzenie

AI Environment Manager to narzędzie umożliwiające łatwe tworzenie, zarządzanie, udostępnianie i klonowanie środowisk programistycznych AI. Dzięki niemu możesz natychmiast rozpocząć pracę nad projektami AI bez konieczności ręcznej konfiguracji środowiska.

## Instalacja

### Wymagania systemowe

- Python 3.8 lub nowszy
- Minimum 4GB RAM
- Minimum 20GB wolnego miejsca na dysku

### Instalacja pakietu

```bash
# Z PyPI
pip install ai-environment-manager

# Lub z repozytorium
git clone https://github.com/ai-environment-manager/ai-environment-manager.git
cd ai-environment-manager
pip install -e .
```

### Pierwsze uruchomienie

```bash
# Inicjalizacja narzędzia
ai-env-manager init

# Uruchomienie interfejsu webowego
ai-env-manager dashboard
```

Po uruchomieniu, interfejs webowy będzie dostępny pod adresem http://localhost:8000.

## Podstawowe pojęcia

### Workspace

Workspace jest głównym kontenerem dla projektów i środowisk. Możesz mieć wiele workspace'ów na jednym komputerze, każdy z własnymi projektami i środowiskami.

### Projekt

Projekt to logiczna jednostka pracy w ramach workspace'u. Każdy projekt może zawierać kod źródłowy, dane, konfiguracje oraz może być powiązany z repozytorium git.

### Środowisko

Środowisko to konfiguracja wykonawcza dla projektów. Może być realizowane jako maszyna wirtualna, kontener lub procesy lokalne. Zawiera definicje narzędzi, bibliotek i zasobów potrzebnych do pracy z projektem.

## Korzystanie z interfejsu webowego

### Dashboard

Dashboard prezentuje przegląd dostępnych workspace'ów, zarówno lokalnych, jak i udostępnionych w sieci.

![Dashboard](images/dashboard.png)

### Zarządzanie workspace'ami

1. **Tworzenie nowego workspace'u**:
   - Kliknij przycisk "Nowy workspace"
   - Podaj nazwę i opcjonalny opis
   - Wybierz szablon lub utwórz pusty workspace

2. **Uruchamianie workspace'u**:
   - Wybierz workspace z listy
   - Kliknij przycisk "Uruchom"
   - System automatycznie uruchomi wszystkie skonfigurowane środowiska

3. **Zatrzymywanie workspace'u**:
   - Wybierz uruchomiony workspace
   - Kliknij przycisk "Zatrzymaj"

4. **Eksportowanie workspace'u**:
   - Wybierz workspace
   - Kliknij "Eksportuj"
   - Wybierz opcje eksportu (z danymi lub bez)
   - Zapisz plik ZIP na dysku

### Zarządzanie projektami

1. **Dodawanie projektu**:
   - Otwórz workspace
   - Kliknij "Dodaj projekt"
   - Podaj nazwę i opis projektu
   - Opcjonalnie podaj URL repozytorium git

2. **Konfiguracja projektu**:
   - Wybierz projekt z listy
   - Edytuj ustawienia (języki, zależności, etc.)
   - Zapisz zmiany

### Zarządzanie środowiskami

1. **Tworzenie środowiska**:
   - Otwórz workspace
   - Kliknij "Dodaj środowisko"
   - Wybierz typ środowiska (VM, kontener, lokalne)
   - Skonfiguruj zasoby i narzędzia

2. **Uruchamianie środowiska**:
   - Wybierz środowisko z listy
   - Kliknij "Uruchom"
   - Po uruchomieniu, dostęp do narzędzi będzie dostępny przez interfejs webowy

## Sieć i udostępnianie

### Wykrywanie środowisk w sieci

System automatycznie wykrywa inne instancje AI Environment Manager w sieci lokalnej. Lista dostępnych zdalnych środowisk jest wyświetlana w sekcji "Sieć" interfejsu webowego.

### Udostępnianie workspace'ów

1. Wybierz workspace z listy
2. Kliknij przycisk "Udostępnij"
3. Workspace będzie widoczny dla innych użytkowników w sieci

### Klonowanie zdalnego workspace'u

1. Przejdź do zakładki "Sieć"
2. Wybierz hosta i workspace do sklonowania
3. Kliknij "Pobierz"
4. Workspace zostanie pobrany i skonfigurowany lokalnie

## Korzystanie z linii poleceń

AI Environment Manager oferuje również interfejs linii poleceń do zarządzania środowiskami.

### Podstawowe komendy

```bash
# Wyświetl listę workspace'ów
ai-env-manager list

# Utwórz nowy workspace
ai-env-manager create my-workspace

# Uruchom workspace
ai-env-manager start my-workspace

# Zatrzymaj workspace
ai-env-manager stop my-workspace

# Wyświetl hosty w sieci
ai-env-manager peers

# Udostępnij workspace
ai-env-manager share my-workspace

# Pobierz workspace z innego hosta
ai-env-manager pull 192.168.1.100 remote-workspace
```

### Zaawansowane komendy

```bash
# Eksportuj workspace do pliku
ai-env-manager export my-workspace --output ~/exported/my-workspace.zip

# Importuj workspace z pliku
ai-env-manager import ~/exported/my-workspace.zip

# Dodaj projekt do workspace'u
ai-env-manager project create my-workspace my-project

# Dodaj środowisko do workspace'u
ai-env-manager env create my-workspace my-env --type vm
```

## Rozwiązywanie problemów

### Diagnostyka

System automatycznie tworzy logi, które można sprawdzić w przypadku problemów:

```bash
# Wyświetl logi
ai-env-manager logs

# Sprawdź status usług
ai-env-manager status
```

### Typowe problemy

1. **Nie można wykryć innych hostów w sieci**:
   - Sprawdź czy zapora sieciowa nie blokuje portów UDP 37777
   - Upewnij się, że komputery są w tej samej sieci lokalnej
   - Sprawdź czy multicast jest włączony w routerze

2. **Nie można uruchomić środowiska**:
   - Sprawdź czy masz wystarczające zasoby systemowe
   - Sprawdź logi systemu
   - Upewnij się, że wymagane narzędzia są zainstalowane (np. libvirt, Docker)

3. **Problemy z interfejsem webowym**:
   - Sprawdź czy serwer API działa (`ai-env-manager status`)
   - Sprawdź logi przeglądarki (Console)
   - Spróbuj wyczyścić cache przeglądarki

## Najlepsze praktyki

1. **Organizacja workspace'ów**:
   - Twórz oddzielne workspace'y dla różnych projektów
   - Używaj tagów do kategoryzacji workspace'ów

2. **Zarządzanie zasobami**:
   - Przydzielaj odpowiednią ilość zasobów do środowisk
   - Zatrzymuj nieużywane środowiska

3. **Udostępnianie i współpraca**:
   - Udostępniaj tylko te workspace'y, które są gotowe do użycia przez innych
   - Używaj deskryptywnych nazw i opisów