ai-environment-manager/
├── bin/                           # Skrypty uruchomieniowe
│   ├── ai-env-manager             # Główny skrypt
│   └── ai-env-quickstart          # Skrypt szybkiego startu
├── src/                           # Kod źródłowy
│   ├── core/                      # Rdzeń systemu
│   │   ├── __init__.py
│   │   ├── config.py              # Zarządzanie konfiguracją
│   │   ├── workspace.py           # Model workspace'u
│   │   ├── environment.py         # Model środowiska
│   │   └── project.py             # Model projektu
│   ├── p2p/                       # Moduł komunikacji peer-to-peer
│   │   ├── __init__.py
│   │   ├── discovery.py           # Wykrywanie węzłów w sieci
│   │   ├── protocol.py            # Protokół komunikacyjny
│   │   └── network.py             # Zarządzanie siecią P2P
│   ├── api/                       # API REST
│   │   ├── __init__.py
│   │   ├── server.py              # Serwer API
│   │   ├── endpoints/             # Endpointy API
│   │   │   ├── __init__.py
│   │   │   ├── workspaces.py      # API workspace'ów
│   │   │   ├── environments.py    # API środowisk
│   │   │   └── discovery.py       # API wykrywania w sieci
│   ├── sharing/                   # Udostępnianie zasobów
│   │   ├── __init__.py
│   │   ├── repository.py          # Repozytorium zasobów
│   │   ├── transfer.py            # Transfer plików
│   │   └── auth.py                # Autoryzacja dostępu
│   ├── runtime/                   # Uruchamianie środowisk
│   │   ├── __init__.py
│   │   ├── vm.py                  # Zarządzanie VM
│   │   ├── container.py           # Zarządzanie kontenerami
│   │   └── process.py             # Zarządzanie procesami lokalnymi
│   ├── web/                       # Interfejs webowy
│   │   ├── __init__.py
│   │   ├── server.py              # Serwer HTTP dla UI
│   │   ├── frontend/              # Pliki frontendu
│   │   │   ├── index.html         # Główny plik HTML
│   │   │   ├── css/               # Style CSS
│   │   │   ├── js/                # Skrypty JS
│   │   │   └── img/               # Obrazy
│   ├── utils/                     # Narzędzia pomocnicze
│   │   ├── __init__.py
│   │   ├── logging.py             # System logowania
│   │   ├── crypto.py              # Kryptografia
│   │   └── system.py              # Narzędzia systemowe
├── docs/                          # Dokumentacja
│   ├── architecture.md            # Architektura systemu
│   ├── user_guide.md              # Przewodnik użytkownika
│   ├── developer_guide.md         # Przewodnik dewelopera
│   └── api_reference.md           # Dokumentacja API
├── tests/                         # Testy
│   ├── __init__.py
│   ├── unit/                      # Testy jednostkowe
│   └── integration/               # Testy integracyjne
├── setup.py                       # Skrypt instalacyjny
├── requirements.txt               # Zależności
└── README.md                      # Główny plik README