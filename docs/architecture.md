# Architektura AI Environment Manager

## Przegląd

AI Environment Manager to modularny system umożliwiający zarządzanie, udostępnianie i klonowanie środowisk programistycznych AI w sieci lokalnej. System działa w architekturze peer-to-peer, pozwalając na automatyczne wykrywanie i udostępnianie środowisk między komputerami bez centralnego serwera.

## Główne komponenty

System składa się z następujących głównych komponentów:

1. **Core** - rdzeń systemu z modelem danych i podstawową funkcjonalnością
2. **P2P Discovery** - moduł wykrywania urządzeń w sieci lokalnej
3. **Sharing & Repository** - moduł udostępniania i pobierania środowisk
4. **Runtime** - moduł uruchamiania i zarządzania środowiskami
5. **API** - REST API umożliwiające komunikację z systemem
6. **Web UI** - interfejs użytkownika dostępny przez przeglądarkę

## Diagram architektury

```
+--------------------+     +--------------------+
|                    |     |                    |
|     Web Browser    |     |    Command Line    |
|                    |     |                    |
+--------+-----------+     +----------+---------+
         |                            |
         v                            v
+--------+--------------------------+-+--------+
|                                              |
|                    Web UI                    |
|                                              |
+----------------------+---------------------+-+
                       |                     |
                       v                     v
+---------------------++                   +-+---------------------+
|                      |                   |                       |
|       REST API       |                   |      WebSocket API    |
|                      |                   |                       |
+------+-+-------------+                   +-------------+---------+
       | |                                               |
       | |                                               |
       | |       +---------------------------+           |
       | |       |                           |           |
       | +------>+      P2P Discovery        +<----------+
       |         |                           |
       |         +---------+----------+------+
       |                   |          |
       v                   v          v
+------+----+      +-------+---+    +-+----------+
|           |      |           |    |            |
|   Core    <----->+  Sharing  <---->  Runtime   |
|           |      |           |    |            |
+-----------+      +-----------+    +------------+
       ^                  ^               ^
       |                  |               |
       v                  v               v
+------+------------------+--------------+------+
|                                                |
|              File System Storage               |
|                                                |
+------------------------------------------------+
```

## Model danych

System opiera się na następującej hierarchii danych:

1. **Workspace** - główny kontener dla projektów i środowisk
   - Można mieć wiele workspace'ów na jednym komputerze
   - Każdy workspace może być niezależnie udostępniany w sieci

2. **Projekt** - logiczna jednostka pracy w ramach workspace'u
   - Może zawierać kod źródłowy, dane, konfiguracje
   - Może być powiązany z repozytoriami git

3. **Środowisko** - konfiguracja wykonawcza dla projektów
   - Może być realizowane jako maszyna wirtualna, kontener lub procesy lokalne
   - Zawiera definicje narzędzi, bibliotek i zasobów

## Przepływ danych

### Wykrywanie i udostępnianie

1. Moduł P2P Discovery automatycznie wykrywa inne instancje systemu w sieci lokalnej
2. Każda instancja rozgłasza informacje o dostępnych środowiskach
3. Repository agreguje informacje o udostępnionych środowiskach
4. Web UI prezentuje listę dostępnych lokalnie i zdalnie środowisk

### Klonowanie środowiska

1. Użytkownik wybiera środowisko do sklonowania
2. Moduł Sharing pobiera i rozpakuje pliki środowiska
3. Core rejestruje nowy workspace w systemie lokalnym
4. Runtime konfiguruje środowisko dostosowując je do lokalnych zasobów

### Uruchamianie środowiska

1. Użytkownik wybiera workspace i środowisko do uruchomienia
2. Core sprawdza zasoby i konfigurację
3. Runtime uruchamia odpowiednie komponenty (VM, kontenery, procesy)
4. API udostępnia informacje o uruchomionym środowisku
5. Web UI prezentuje linki do dostępu do narzędzi

## Protokoły komunikacji

System wykorzystuje następujące protokoły:

1. **UDP Multicast** - do wykrywania urządzeń w sieci lokalnej
2. **HTTP/REST** - do API i pobierania zasobów
3. **WebSocket** - do komunikacji w czasie rzeczywistym z interfejsem użytkownika
4. **SSH/SCP** - do zdalnego uruchamiania i zarządzania środowiskami (opcjonalnie)

## Bezpieczeństwo

1. Domyślnie system działa tylko w sieci lokalnej
2. Opcjonalnie można zabezpieczyć API kluczem API
3. Transfery danych mogą być szyfrowane
4. Uwierzytelnianie dostępu do udostępnionych środowisk

## Skalowalność

System wspiera różne scenariusze wdrożenia:

1. **Standalone** - pojedyncza instancja na komputerze
2. **Workgroup** - wiele instancji w sieci lokalnej
3. **Federation** - współdzielenie obciążeń między wieloma instancjami