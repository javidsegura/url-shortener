.PHONY: help dev dev-debug install db-models lint lint-check pytest-run  test-docker-compose-start

SHELL := /bin/bash

# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

.DEFAULT_GOAL := help

# Variables
VENV = ../.venv
VENV_ACTIVATE = source $(VENV)/bin/activate
APP_PATH = src.url_shortener.main:app
PORT = 8000
BACKEND_ENV_FILE_SYNCED_PATH= ../backend/env_config/synced/.env.$(ENVIRONMENT)
PROJECT_NAME = url-shortener



help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)


# 0) Set-up
install: ## Install backend dependencies
	python3.11 -m venv $(VENV)
	$(VENV_ACTIVATE) && pip3 install -e "."
	$(VENV_ACTIVATE) && alembic init migrations || echo "alembic init already started"
install-full: ## Install backend dependices for client + dev usage
	python3.11 -m venv $(VENV)
	$(VENV_ACTIVATE) && pip3 install -e ".[dev, tests]"
	$(VENV_ACTIVATE) && alembic init migrations || echo "alembic init already started"


# 1) Boot-up 
dev: ## Start backend development server
	$(VENV_ACTIVATE) &&  ENVIRONMENT=dev uvicorn $(APP_PATH) --reload --host 0.0.0.0 --port $(PORT)



# 2) CI
lint: ## Run linting and formatting (local dev)
	@echo "$(YELLOW)Running linting and formatting...$(RESET)"
	@echo "$(BLUE)Formatting code with ruff...$(RESET)"
	$(VENV_ACTIVATE) && ruff format src/
	@echo "$(BLUE)Running ruff checks and fixes...$(RESET)"
	$(VENV_ACTIVATE) && ruff check --fix src/

lint-check: ## Run linting checks (CI)
	@echo "$(YELLOW)Running CI linting checks...$(RESET)"
	@echo "$(BLUE)Checking code formatting with ruff...$(RESET)"
	@$(VENV_ACTIVATE) && ruff format --check src/
	@echo "$(BLUE)Running ruff checks...$(RESET)"
	@$(VENV_ACTIVATE) && ruff check  src/
	@echo "$(BLUE)Running ruff checks with diff...$(RESET)"
	@$(VENV_ACTIVATE) && ruff check  --diff --fix src/ 

format: ## Formats
	@echo "$(YELLOW)Running CI formatting$(RESET)"
	@echo "$(BLUE)Checking code formatting with ruff...$(RESET)"
	@$(VENV_ACTIVATE) && ruff format --check src/

format-fix: ## Format code (for pre-commit)
	@echo "$(YELLOW)Formatting code with ruff...$(RESET)"
	$(VENV_ACTIVATE) && ruff format src/
	


static-security-analysis: ## Run static security analysis
	@echo "$(BLUE)Running security checks with bandit...$(RESET)"
	$(VENV_ACTIVATE) && bandit -r src/ -f json -o bandit-report.json || true
	@echo "$(BLUE)Running security checks with safety...$(RESET)"
	$(VENV_ACTIVATE) && safety check --json || true


# 3) CD
## DB
db-create-migration-files:
	@if [ -z "$(MESSAGE)" ]; then echo "❌ Please provide MESSAGE='your description'"; exit 1; fi
	
	ENVIRONMENT=dev.local && $(VENV_ACTIVATE) && alembic revision --autogenerate -m "$(MESSAGE)"


db-test-migration: ## Dev
	$(MAKE) db-create-migration-files
	$(VENV_ACTIVATE) && alembic upgrade head


db-safe-migration: ## Prod
	@echo "🔍 Pre-deployment checks..."
	$(VENV_ACTIVATE) && alembic check || (echo "❌ Validation failed!"; exit 1)
	@echo "Current status:"
	$(VENV_ACTIVATE) && alembic current
	@echo "Pending migrations:"
	$(VENV_ACTIVATE) && alembic history --verbose | head -10
	@echo ""
	$(VENV_ACTIVATE) && alembic upgrade head
	@echo "✅ Production deployment complete!"


db-downgrade-prior-version:
	$(VENV_ACTIVATE) && alembic downgrade -1

db-downgrade-specific-version:
	$(VENV_ACTIVATE) && alembic downgrade $(MIGRATION_ID)


push_docker: ## Push Docker image with version tag
	$(MAKE) check_enviroment_variables
	@if [ -z "$(BACKEND_VERSION)" ]; then \
		echo "ERROR: BACKEND_TAG variable is required. Usage: make push_docker BACKEND_TAG=v1.2.3"; \
		exit 1; \
	fi
	docker login
	docker buildx build \
		-t javidsegura/url_shortener_backend:$(ENVIRONMENT)-$(BACKEND_VERSION) \
		-t javidsegura/url_shortener_backend:$(ENVIRONMENT) \
		--platform linux/amd64,linux/arm64 \
		--push \
		-f ./Dockerfile ./
	@echo "✓ Pushed images:"
	@echo "  - javidsegura/url_shortener_backend:$(ENVIRONMENT)-$(BACKEND_VERSION)"
	@echo "  - javidsegura/url_shortener_backend:$(ENVIRONMENT)"

# 4) Tests
pytest-run:
	$(VENV_ACTIVATE) && pytest -s -vv \
					--cov=url_shortener \
					--cov-report=term-missing \
					test/integration/endpoints/


unit-test: ## Run all unit tests
	@echo "$(YELLOW)Running all tests...$(RESET)"
	$(VENV_ACTIVATE) && python3 -m pytest test/unit/database -v

integration-test: ## Runn all integration tests
	$(VENV_ACTIVATE) && python3 -m pytest -s -vv test/integration/endpoints
	

test-docker-compose-start: ## Stats docker compose for integration tests of endpoints
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f ../docker-compose.yml -f ../docker-compose.test.yml -p $(PROJECT_NAME) up --build 

test-docker-compose-stop: ## Stops docker compose for integration tests of endpoints
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f ../docker-compose.yml -f ../docker-compose.test.yml -p $(PROJECT_NAME) down -v

# 5) Miscellaneous
check_enviroment_variables:
	@if [ -z "$$ENVIRONMENT" ]; then \
		echo "Error: ENVIRONMENT must be defined"; \
		exit 1; \
	fi
	echo "Environment is: $(ENVIRONMENT)"

# 6) Docker
push_docker: ## Push Docker image with version tag
	$(MAKE) check_enviroment_variables
	@if [ -z "$(BACKEND_VERSION)" ]; then \
		echo "$(RED)ERROR: BACKEND_VERSION required$(RESET)"; \
		echo "Usage: make push_docker BACKEND_VERSION=v1.0.0"; \
		exit 1; \
	fi
	docker buildx build \
		-t javidsegura/url_shortener_backend:$(ENVIRONMENT)-$(BACKEND_VERSION) \
		-t javidsegura/url_shortener_backend:$(ENVIRONMENT) \
		--platform linux/amd64,linux/arm64 \
		--push \
		-f ./Dockerfile ./
	@echo "$(GREEN)✓ Pushed: $(ENVIRONMENT)-$(BACKEND_VERSION)$(RESET)"