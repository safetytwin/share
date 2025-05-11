# Makefile for twinshare project

# Variables
PYTHON := python3
VENV_DIR := venv
PYTHON_VENV := $(VENV_DIR)/bin/python
PIP_VENV := $(VENV_DIR)/bin/pip
PROJECT_DIR := $(shell pwd)
LOG_DIR := /tmp/twinshare/logs
RUN_DIR := /tmp/twinshare/run
API_PORT := 37780
API_HOST := 0.0.0.0

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# Default target
.PHONY: help
help:
	@echo "$(GREEN)Twinshare Project Makefile$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make <target>"
	@echo ""
	@echo "$(YELLOW)Targets:$(NC)"
	@echo "  $(GREEN)help$(NC)        - Show this help message"
	@echo "  $(GREEN)setup$(NC)       - Set up the development environment"
	@echo "  $(GREEN)install$(NC)     - Install the package in development mode"
	@echo "  $(GREEN)start-api$(NC)   - Start the REST API server"
	@echo "  $(GREEN)stop-api$(NC)    - Stop the REST API server"
	@echo "  $(GREEN)restart-api$(NC) - Restart the REST API server"
	@echo "  $(GREEN)test-api$(NC)    - Test the API endpoints"
	@echo "  $(GREEN)test-cli$(NC)    - Test the CLI commands"
	@echo "  $(GREEN)clean$(NC)       - Clean up temporary files"

# Setup the development environment
.PHONY: setup
setup:
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@mkdir -p $(LOG_DIR)
	@mkdir -p $(RUN_DIR)
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(GREEN)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "$(GREEN)Installing dependencies...$(NC)"
	@$(PIP_VENV) install -e .
	@echo "$(GREEN)Setup complete.$(NC)"

# Install the package in development mode
.PHONY: install
install:
	@echo "$(GREEN)Installing package in development mode...$(NC)"
	@$(PIP_VENV) install -e .
	@echo "$(GREEN)Installation complete.$(NC)"

# Start the REST API server
.PHONY: start-api
start-api:
	@echo "$(GREEN)Starting REST API server...$(NC)"
	@mkdir -p $(LOG_DIR)
	@mkdir -p $(RUN_DIR)
	@if pgrep -f "simple_api_server.py" > /dev/null; then \
		echo "$(YELLOW)API server is already running.$(NC)"; \
	else \
		PYTHONPATH=$(PROJECT_DIR) $(PYTHON) $(PROJECT_DIR)/simple_api_server.py > $(LOG_DIR)/api.log 2>&1 & \
		echo $$! > $(RUN_DIR)/api.pid; \
		echo "$(GREEN)API server started with PID $$(cat $(RUN_DIR)/api.pid)$(NC)"; \
		echo "$(GREEN)API is available at: http://$(API_HOST):$(API_PORT)$(NC)"; \
		echo "$(GREEN)Log file: $(LOG_DIR)/api.log$(NC)"; \
	fi

# Stop the REST API server
.PHONY: stop-api
stop-api:
	@echo "$(GREEN)Stopping REST API server...$(NC)"
	@if [ -f "$(RUN_DIR)/api.pid" ]; then \
		PID=$$(cat $(RUN_DIR)/api.pid); \
		if ps -p $$PID > /dev/null; then \
			echo "$(GREEN)Stopping API server with PID $$PID$(NC)"; \
			kill $$PID; \
			sleep 2; \
			if ps -p $$PID > /dev/null; then \
				echo "$(YELLOW)Force stopping API server...$(NC)"; \
				kill -9 $$PID; \
			fi; \
		else \
			echo "$(YELLOW)API server is not running with PID $$PID$(NC)"; \
		fi; \
		rm -f $(RUN_DIR)/api.pid; \
	else \
		echo "$(YELLOW)No API server PID file found.$(NC)"; \
		pkill -f "simple_api_server.py" || true; \
	fi

# Restart the REST API server
.PHONY: restart-api
restart-api:
	@echo "$(GREEN)Restarting REST API server...$(NC)"
	@$(MAKE) stop-api
	@sleep 2
	@$(MAKE) start-api

# Test the API endpoints
.PHONY: test-api
test-api:
	@echo "$(GREEN)Testing API endpoints...$(NC)"
	@echo "$(GREEN)Testing root endpoint...$(NC)"
	@curl -s http://$(API_HOST):$(API_PORT)/ | python3 -m json.tool || echo "$(RED)Failed to connect to API server$(NC)"
	@echo "$(GREEN)Testing /shared endpoint...$(NC)"
	@curl -s http://$(API_HOST):$(API_PORT)/shared | python3 -m json.tool || echo "$(RED)Failed to connect to API server$(NC)"
	@echo "$(GREEN)Testing /shared/my_workspace endpoint (POST)...$(NC)"
	@curl -s -X POST http://$(API_HOST):$(API_PORT)/shared/my_workspace \
		-H "Content-Type: application/json" \
		-d '{"enable": true}' | python3 -m json.tool || echo "$(RED)Failed to connect to API server$(NC)"
	@echo "$(GREEN)Testing /shared/my_workspace endpoint (DELETE)...$(NC)"
	@curl -s -X DELETE http://$(API_HOST):$(API_PORT)/shared/my_workspace | python3 -m json.tool || echo "$(RED)Failed to connect to API server$(NC)"

# Test the CLI commands
.PHONY: test-cli
test-cli:
	@echo "$(GREEN)Testing CLI commands...$(NC)"
	@echo "$(GREEN)Testing workspace list command...$(NC)"
	@PYTHONPATH=$(PROJECT_DIR) $(PYTHON) -m src.cli.main workspace list
	@echo "$(GREEN)Testing workspace share command...$(NC)"
	@PYTHONPATH=$(PROJECT_DIR) $(PYTHON) -m src.cli.main workspace share --name my_workspace
	@echo "$(GREEN)Testing workspace unshare command...$(NC)"
	@PYTHONPATH=$(PROJECT_DIR) $(PYTHON) -m src.cli.main workspace unshare --name my_workspace
	@echo "$(GREEN)Testing remote vm-list command...$(NC)"
	@PYTHONPATH=$(PROJECT_DIR) $(PYTHON) -m src.cli.main remote vm-list --peer 127.0.0.1 || echo "$(YELLOW)Command failed, but this is expected if no peer is available$(NC)"

# Clean up temporary files
.PHONY: clean
clean:
	@echo "$(GREEN)Cleaning up temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "*.egg" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".coverage" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name ".tox" -exec rm -rf {} +
	@echo "$(GREEN)Cleanup complete.$(NC)"
