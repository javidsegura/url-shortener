.PHONY: help dev dev-debug install db-models lint lint-check test 

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
APP_PATH = src.main:app
PORT = 8000


help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)


# 0) Set-up
install: ## Install backend dependencies
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
	@echo "$(BLUE)Running security checks with bandit...$(RESET)"
	$(VENV_ACTIVATE) && bandit -r src/

lint-check: ## Run linting checks (CI)
	@echo "$(YELLOW)Running CI linting checks...$(RESET)"
	@echo "$(BLUE)Checking code formatting with ruff...$(RESET)"
	@$(VENV_ACTIVATE) && ruff format --check src/
	@echo "$(BLUE)Running ruff checks...$(RESET)"
	@$(VENV_ACTIVATE) && ruff check  src/
	@echo "$(BLUE)Running ruff checks with diff...$(RESET)"
	@$(VENV_ACTIVATE) && ruff check  --diff --fix src/ 
	@echo "$(BLUE)Running security checks with bandit...$(RESET)"
	@$(VENV_ACTIVATE) && bandit -r src/ 

test: ## Run all tests
	@echo "$(YELLOW)Running all tests...$(RESET)"
	$(VENV_ACTIVATE) && python3 -m pytest test/unit/links.py -v

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


push_docker: ## MOVE ME TO BAckend
	$(MAKE) check_enviroment_variables
	docker login
	docker buildx build -t javidsegura/url_shortener_backend:$(ENVIRONMENT) --platform linux/amd64,linux/arm64 --push -f ./Dockerfile ./


check_enviroment_variables:
	@if [ -z "$$ENVIRONMENT" ]; then \
		echo "Error: ENVIRONMENT must be defined"; \
		exit 1; \
	fi
	echo "Environment is: $(ENVIRONMENT)"

# Tests
pytest-run:
	$(VENV_ACTIVATE) && PYTEST_RUNNING=true pytest -s -vv \
					--cov=url_shortener \
					--cov-report=term-missing \
					test/unit