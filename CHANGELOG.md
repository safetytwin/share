# Changelog

All notable changes to this project will be documented in this file.

## [0.1.47] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in p2p_test.py
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.46] - 2025-05-11

### Added
- Changes in .gitignore
- Changes in Dockerfile.p2ptest
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in run_terraform_ansible_test.sh
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.45] - 2025-05-11

### Added
- Changes in .gitignore
- Changes in Dockerfile.p2ptest
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in run_terraform_ansible_test.sh
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.44] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.43] - 2023-05-11
### Fixed
- Fixed P2P discovery in Docker network by adding manual peer discovery
- Updated Dockerfile.p2ptest to correctly specify TCP port for 47778
- Added Ansible configuration to fix permission issues with temporary directories
- Improved run script to use temporary directories for Terraform state files
- Fixed zeroconf service browser implementation for better peer discovery

## [0.1.42] - 2023-05-10
### Changed
- Changed log file location from `/var/log/p2p_test.log` to `logs/p2p_test.log` to avoid permission issues
- Updated port numbers from 37777/37778 to 47777/47778 across all configurations
- Made dependencies (netifaces, zeroconf) optional with graceful fallbacks
- Improved error handling in P2P test script

### Added
- Added automatic creation of logs directory
- Added main function to p2p_test.py for better structure
- Added port conflict detection to run script

## [0.1.41] - 2023-05-09
### Added
- Initial implementation of P2P testing infrastructure
- Added Terraform configuration for Docker containers
- Added Ansible playbook for test automation
- Created Dockerfile for P2P test environment

## [0.1.40] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.39] - 2025-05-11

### Added
- Changes in Dockerfile
- Changes in docker-compose.yml
- Changes in docker-entrypoint.sh
- Changes in p2p_test.py
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in test-p2p.sh

### Changed
- Changes in run_p2p_test.sh

## [0.1.38] - 2025-05-11

### Added
- Changes in Dockerfile
- Changes in docker-entrypoint.sh
- Changes in docs/p2p_networking.md
- Changes in docs/rest_api_guide.md
- Changes in docs/vm_sharing_guide.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

### Changed
- Changes in test-p2p.sh

## [0.1.37] - 2025-05-11

### Added
- Changes in docs/p2p_networking.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/cli/commands.py
- Changes in src/p2p/discovery.py
- Changes in src/p2p/network.py

## [0.1.36] - 2025-05-11

### Added
- Changes in README.md
- Changes in docs/rest_api_guide.md
- Changes in docs/vm_sharing_guide.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

### Changed
- Changes in docs/index.md

## [0.1.35] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/p2p/network.py

## [0.1.34] - 2025-05-11

### Added
- Changes in README.md
- Changes in docs/rest_api_guide.md
- Changes in docs/vm_sharing_guide.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/p2p/discovery.py
- Changes in src/p2p/network.py

## [0.1.33] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in src/cli/commands.py

### Changed
- Changes in src/cli/commands.py.bak

## [0.1.32] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in src/cli/commands.py

### Changed
- Changes in src/cli/commands.py.bak

## [0.1.31] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in src/cli/commands.py

### Changed
- Changes in src/cli/commands.py.bak

## [0.1.30] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in src/cli/commands.py

## [0.1.29] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in src/cli/commands.py

## [0.1.28] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.27] - 2025-05-11

### Added
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py

## [0.1.26] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/cli/main.py

## [0.1.25] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in twinshare_cli.py

## [0.1.24] - 2025-05-11

### Added
- Changes in MANIFEST.in
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/cli/commands.py

## [0.1.23] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/cli/__init__.py
- Changes in src/cli/main.py

## [0.1.22] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.21] - 2025-05-11

### Added
- Changes in README.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py

### Changed
- Changes in MANIFEST.in

## [0.1.20] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/cli/main.py
- Changes in twinshare

## [0.1.19] - 2025-05-11

### Added
- Changes in bin/twinshare
- Changes in install_package.sh
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/__init__.py

## [0.1.18] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.17] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.16] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in requirements.txt
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.15] - 2025-05-11

### Added
- Changes in README.md
- Changes in bin/twinshare
- Changes in docs/vm_sharing_guide.md
- Changes in install_package.sh
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

## [0.1.14] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak

### Changed
- Changes in bin/twinshare

## [0.1.13] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/cli/commands.py

### Changed
- Changes in run_api_direct.py

## [0.1.12] - 2025-05-11

### Added
- Changes in docs/service_installation.md
- Changes in docs/troubleshooting.md
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in scripts/start_rest_api.py
- Changes in scripts/twinshare-rest-api.service
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/api/rest_server.py
- Changes in src/core/config.py
- Changes in src/runtime/vm.py
- Changes in twinshare

### Changed
- Changes in fix_cli_command.sh

## [0.1.11] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in README.md
- Changes in examples/api_usage.py
- Changes in examples/cli_usage.md
- Changes in examples/rest_api_usage.py
- Changes in install.sh
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py
- Changes in setup.py.bak
- Changes in src/core/config.py
- Changes in start_service.sh

### Changed
- Changes in =0.7.0
- Changes in docs/example_vm_sharing.md
- Changes in fix_ssl_config.sh

## [0.1.10] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in setup.py
- Changes in src/api/server.py
- Changes in src/web/server.py

### Changed
- Changes in pyproject.toml.bak
- Changes in setup.py.bak

## [0.1.9] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in setup.py
- Changes in src/api/server.py
- Changes in src/web/server.py

### Changed
- Changes in pyproject.toml.bak
- Changes in setup.py.bak

## [0.1.8] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in setup.py
- Changes in src/api/server.py
- Changes in src/web/server.py

### Changed
- Changes in pyproject.toml.bak
- Changes in setup.py.bak

## [0.1.7] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in pyproject.toml
- Changes in setup.py
- Changes in src/api/server.py
- Changes in src/web/server.py

### Changed
- Changes in pyproject.toml.bak
- Changes in setup.py.bak

## [0.1.6] - 2025-05-11

### Added
- Changes in pyproject.toml
- Changes in setup.py
- Changes in src/web/server.py

### Changed
- Changes in =0.7.0
- Changes in pyproject.toml.bak
- Changes in setup.py.bak

## [0.1.5] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in docs/service_installation.md
- Changes in setup.py
- Changes in src/api/__init__.py
- Changes in src/api/endpoints/discovery.py
- Changes in src/api/endpoints/environments.py
- Changes in src/api/endpoints/workspaces.py
- Changes in src/api/p2p_api.py
- Changes in src/api/rest_client.py
- Changes in src/api/rest_server.py
- Changes in src/api/server.py
- Changes in src/api/vm_api.py
- Changes in src/cli/__init__.py
- Changes in src/cli/commands.py
- Changes in src/cli/main.py
- Changes in src/core/config.py
- Changes in src/core/environment.py
- Changes in src/core/project.py
- Changes in src/core/workspace.py
- Changes in src/p2p/discovery.py
- Changes in src/p2p/network.py
- Changes in src/p2p/protocol.py
- Changes in src/runtime/container.py
- Changes in src/runtime/process.py
- Changes in src/runtime/vm.py
- Changes in src/runtime/vm.py.bak
- Changes in src/sharing/auth.py
- Changes in src/sharing/repository.py
- Changes in src/sharing/transfer.py
- Changes in src/utils/crypto.py
- Changes in src/utils/logging.py
- Changes in src/utils/system.py
- Changes in src/web/server.py

### Changed
- Changes in =0.7.0
- Changes in fix_aiohttp.sh
- Changes in fix_service.sh
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in tests/unit/test_basic.py

## [0.1.4] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in docs/service_installation.md
- Changes in setup.py

### Changed
- Changes in =0.7.0
- Changes in fix_aiohttp.sh
- Changes in fix_service.sh
- Changes in pyproject.toml
- Changes in pyproject.toml.bak
- Changes in setup.py.bak
- Changes in src/__init__.py
- Changes in tests/unit/test_basic.py

## [0.1.3] - 2025-05-11

### Added
- Changes in CHANGELOG.md
- Changes in docs/service_installation.md
- Changes in setup.py

### Changed
- Changes in =0.7.0
- Changes in fix_aiohttp.sh
- Changes in fix_service.sh
- Changes in setup.py.bak
- Changes in tests/unit/test_basic.py

## [0.1.2] - 2025-05-11

### Added
- Changes in setup.py

### Changed
- Changes in =0.7.0
- Changes in fix_aiohttp.sh
- Changes in fix_service.sh
- Changes in setup.py.bak

## [0.1.1] - 2025-05-11

### Added
- Changes in README.md
- Changes in install.sh
- Changes in requirements.txt
- Changes in scripts/twinshare-rest-api.service
- Changes in setup.py
- Changes in start_service.sh

### Changed
- Changes in setup.py.bak
