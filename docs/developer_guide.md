# Prompty dla dalszego rozwoju projektu AI Environment Manager

Poniżej znajdują się gotowe prompty, które możesz użyć do dalszego rozwoju poszczególnych elementów projektu AI Environment Manager. Skopiuj wybrany prompt i dostosuj go do swoich potrzeb.

## 1. Prompty dla modułu Runtime

### Implementacja modułu obsługi maszyn wirtualnych (VM)

```
Stwórz moduł 'src/runtime/vm.py' do zarządzania maszynami wirtualnymi dla AI Environment Manager. Moduł powinien:

1. Implementować klasę VMRuntime do zarządzania cyklem życia maszyn wirtualnych libvirt/KVM
2. Obsługiwać podstawowe operacje: tworzenie, uruchamianie, zatrzymywanie i usuwanie VM
3. Automatycznie konfigurować sieć dla VM
4. Udostępniać metody do mapowania portów dla usług (VSCode, Jupyter, itd.)
5. Wspierać zaawansowane funkcje jak klonowanie VM i przydzielanie GPU
6. Być zgodny z interfejsem zaproponowanym w architekturze

Zwróć uwagę na obsługę błędów i odpowiednie logowanie operacji. Kod powinien być modularny i dobrze udokumentowany.
```

### Implementacja modułu obsługi kontenerów

```
Zaimplementuj moduł 'src/runtime/container.py' do zarządzania kontenerami Docker/Podman dla AI Environment Manager. Moduł powinien:

1. Obsługiwać Docker oraz Podman jako alternatywne backendy
2. Implementować klasę ContainerRuntime do zarządzania kontenerami
3. Automatycznie generować pliki docker-compose.yml na podstawie konfiguracji
4. Udostępniać metody do bezpiecznego współdzielenia danych między kontenerami
5. Obsługiwać uruchamianie kontenerów z dostępem do GPU
6. Być kompatybilny z federated mode (rozproszonym uruchamianiem kontenerów w sieci)

Zwróć uwagę na izolację środowisk i bezpieczeństwo. Kod powinien być zgodny z architekturą projektu.
```

### Implementacja modułu zarządzania lokalnymi procesami

```
Zaimplementuj moduł 'src/runtime/process.py' do zarządzania lokalnymi procesami dla AI Environment Manager. Moduł powinien:

1. Implementować klasę ProcessRuntime do zarządzania lokalnymi procesami
2. Obsługiwać środowiska Pythona (venv, conda)
3. Zarządzać procesami w tle (uruchamianie serwerów VSCode, Jupyter, itp.)
4. Monitorować stan procesów i automatycznie restartować w razie awarii
5. Zbierać logi z procesów i udostępniać je przez API
6. Obsługiwać zależności między procesami (kolejność uruchamiania)

Zadbaj o przenośność między systemami operacyjnymi (Linux, macOS, Windows).
```

## 2. Prompty dla modułu Sharing

### Implementacja modułu repozytorium

```
Zaimplementuj moduł 'src/sharing/repository.py' do zarządzania udostępnionymi środowiskami AI. Moduł powinien:

1. Implementować klasę Repository do zarządzania metadanymi udostępnionych workspace'ów
2. Obsługiwać rejestrację, aktualizację i wyrejestrowanie workspace'ów
3. Synchronizować informacje o udostępnionych środowiskach z modułem P2P Discovery
4. Implementować metody filtrowania i wyszukiwania środowisk
5. Obsługiwać autoryzację dostępu do środowisk
6. Monitorować i raportować statystyki wykorzystania

Zwróć uwagę na efektywność przechowywania danych i obsługę metadanych środowisk.
```

### Implementacja modułu transferu

```
Zaimplementuj moduł 'src/sharing/transfer.py' do transferu plików przy udostępnianiu środowisk. Moduł powinien:

1. Implementować klasę TransferManager do zarządzania transferami plików
2. Obsługiwać protokoły HTTP i P2P do pobierania i wysyłania plików
3. Implementować mechanizmy wznowienia przerwanych transferów
4. Obsługiwać progresywne pobieranie dużych plików z raportowaniem postępu
5. Implementować weryfikację integralności pobranych plików
6. Obsługiwać kompresję i szyfrowanie transferów

Zadbaj o obsługę błędów sieciowych i odpowiednie raportowanie statusu transferów.
```

## 3. Prompty dla modułu Web

### Implementacja frontendu w React

```
Stwórz frontend aplikacji webowej dla AI Environment Manager w React.js. Frontend powinien:

1. Implementować nowoczesny, responsywny interfejs użytkownika
2. Obsługiwać widoki dla zarządzania workspace'ami, projektami i środowiskami
3. Zawierać komponent wykrywania i wyświetlania sieci P2P
4. Implementować interaktywne formularze do konfiguracji środowisk
5. Obsługiwać monitorowanie i wyświetlanie statusu uruchomionych środowisk
6. Zawierać widok terminala i przeglądarki plików dla projektów
7. Wspierać tryb ciemny i jasny oraz personalizację interfejsu

Wykorzystaj nowoczesne praktyki React (hooks, context API) i zoptymalizuj zarządzanie stanem aplikacji.
```

### Implementacja serwera WebSocket

```
Zaimplementuj serwer WebSocket 'src/web/websocket.py' dla AI Environment Manager. Serwer powinien:

1. Implementować komunikację real-time między backendem a frontendem
2. Obsługiwać powiadomienia o zmianach statusu środowisk
3. Transmitować logi z uruchomionych środowisk w czasie rzeczywistym
4. Obsługiwać terminal webowy dla środowisk
5. Implementować mechanizm autoryzacji połączeń
6. Być skalowalny i obsługiwać wielu klientów jednocześnie

Zapewnij odporność na zrywanie połączeń i automatyczne reconnecty. Kod powinien być zgodny z architekturą projektu.
```

## 4. Prompty dla testów

### Implementacja testów jednostkowych

```
Stwórz komplet testów jednostkowych dla AI Environment Manager. Testy powinny:

1. Testować wszystkie kluczowe klasy i funkcje w modułach core, p2p, sharing i runtime
2. Wykorzystywać mocks i stubs do izolacji testowanych komponentów
3. Obejmować scenariusze pozytywne i obsługę błędów
4. Być zautomatyzowane i uruchamialne przez CI/CD
5. Generować raport pokrycia kodu testami
6. Być zgodne z pytest i zawierać fixtures dla wspólnych scenariuszy

Zwróć szczególną uwagę na testowanie skomplikowanych interakcji między modułami i obsługę warunków brzegowych.
```

### Implementacja testów integracyjnych

```
Stwórz zestaw testów integracyjnych dla AI Environment Manager. Testy powinny:

1. Testować integrację między modułami (core, p2p, sharing, runtime, api)
2. Obejmować scenariusze end-to-end jak tworzenie i uruchamianie środowisk
3. Testować komunikację sieciową P2P z wykorzystaniem wirtualnych węzłów
4. Sprawdzać poprawność interakcji z API i WebUI
5. Testować współpracę z systemami zewnętrznymi (libvirt, docker, itp.)
6. Zawierać testy wydajnościowe dla krytycznych operacji

Zadbaj o izolację testów i możliwość uruchamiania ich w środowisku CI/CD.
```

## 5. Prompty dla dokumentacji

### Dokumentacja API

```
Stwórz kompletną dokumentację API dla AI Environment Manager. Dokumentacja powinna:

1. Opisywać wszystkie endpointy REST API z parametrami, kodami odpowiedzi i przykładami
2. Zawierać informacje o modelu danych i strukturach JSON
3. Dokumentować protokoły komunikacji (REST, WebSocket)
4. Zawierać informacje o autoryzacji i zabezpieczeniach
5. Być zgodna ze standardem OpenAPI 3.0
6. Zawierać przykłady użycia API w różnych językach (curl, Python, JavaScript)

Dokumentacja powinna być przejrzysta i zawierać przykłady dla typowych scenariuszy użycia.
```

### Dokumentacja wdrożeniowa

```
Stwórz dokumentację wdrożeniową dla AI Environment Manager. Dokumentacja powinna:

1. Opisywać wymagania systemowe i zależności
2. Zawierać szczegółowe instrukcje instalacji dla różnych systemów operacyjnych
3. Opisywać konfigurację systemu (zmienne środowiskowe, pliki konfiguracyjne)
4. Zawierać instrukcje wdrożenia w różnych scenariuszach (standalone, workgroup, federation)
5. Dokumentować procedury aktualizacji i migracji danych
6. Opisywać zabezpieczanie instalacji i zalecane praktyki

Dokumentacja powinna być zorganizowana w logiczne sekcje i zawierać rozwiązania typowych problemów.
```

## 6. Prompty dla uruchamiania i integracji

### Skrypt uruchomieniowy

```
Stwórz główny skrypt uruchomieniowy 'bin/ai-env-manager' dla AI Environment Manager. Skrypt powinien:

1. Obsługiwać wszystkie komendy CLI (init, list, create, start, stop, itp.)
2. Implementować parser argumentów z help tekstami
3. Wykonywać sprawdzanie zależności i środowiska
4. Obsługiwać zarządzanie konfiguracją i workspace'ami
5. Obsługiwać logowanie z różnymi poziomami szczegółowości
6. Zapewniać interfejs do wszystkich funkcji systemu

Skrypt powinien być użytkownikowi przyjazny, z czytelnym wyświetlaniem błędów i podpowiedziami.
```

### Skrypt integracyjny z IDE

```
Stwórz skrypt/plugin do integracji AI Environment Manager z popularnymi IDE (VSCode, PyCharm). Rozwiązanie powinno:

1. Umożliwiać zarządzanie workspace'ami bezpośrednio z IDE
2. Automatycznie konfigurować interpreter/runtime dla projektu na podstawie środowiska
3. Umożliwiać uruchamianie i zatrzymywanie środowisk
4. Synchronizować pliki projektu ze środowiskiem
5. Zapewniać dostęp do konsoli i logów środowiska
6. Obsługiwać debugowanie kodu w środowisku

Rozwiązanie powinno być łatwe w instalacji i konfiguracji, z odpowiednią dokumentacją.
```

## 7. Prompty dla funkcji specyficznych

### Implementacja logiki federated mode

```
Zaimplementuj funkcjonalność Federation Mode dla AI Environment Manager, inspirowaną rozwiązaniem z LocalAI. Funkcja powinna:

1. Umożliwiać rozproszenie obciążeń między wieloma węzłami w sieci
2. Automatycznie zarządzać kierowaniem zapytań do odpowiednich węzłów
3. Obsługiwać balansowanie obciążenia i failover
4. Synchronizować stan środowisk między węzłami
5. Wspierać dynamiczne dołączanie i odłączanie węzłów
6. Obsługiwać autoryzację między węzłami w federacji

Funkcja powinna być zgodna z architekturą projektu i łatwa w konfiguracji.
```

### Implementacja automatycznego klonowania repozytoriów git

```
Zaimplementuj funkcję automatycznego klonowania repozytoriów git przy pobieraniu workspace'ów. Funkcja powinna:

1. Automatycznie wykrywać repozytoria git powiązane z projektami
2. Obsługiwać różne protokoły (HTTPS, SSH)
3. Wspierać uwierzytelnianie (kredencjale, klucze SSH)
4. Konfigurować git-hooks dla automatycznej synchronizacji
5. Obsługiwać zarządzanie gałęziami i submodułami
6. Integrować się z modułem workspace'ów i projektów

Funkcja powinna być konfigurowalna i bezpieczna w obsłudze kredencjali.
```