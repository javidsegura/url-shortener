.PHONY: help dev install
.DEFAULT_GOAL := help

# VARIABLES
# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

BACKEND_ENV_FILE_SYNCED_PATH = ./backend/env_config/synced/.env.$(ENVIRONMENT)
FROTNEND_ENV_FILE_SYNCED_PATH = ./frontend/env_config/synced/.env.$(ENVIRONMENT)
TERRAFORM_PATH = ./infra/terraform/environment/$(ENVIRONMENT)
PROJECT_NAME = url-shortener


help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install project-wide dependencies
	@echo "$(YELLOW)Installing all project dependencies...$(RESET)"
	$(MAKE) check_enviroment_variables
	$(MAKE) -C backend install
	$(MAKE) -C frontend install
	$(MAKE) -C infra install
	brew install jq
install-packages: ## Install only packages
	@echo "$(YELLOW)Installing all project dependencies...$(RESET)"
	$(MAKE) check_enviroment_variables
	$(MAKE) -C backend install
	$(MAKE) -C frontend install


dev-start: ## Hot reload enabled
	$(MAKE) check_enviroment_variables
	$(MAKE) -C infra terraform-apply
	$(MAKE) -C infra sync_envs
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) up --build 
	$(MAKE) container_logs SERVICE_NAME=backend

dev-stop: ## Stop development environment
	$(MAKE) check_enviroment_variables
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH)  docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) down -v
	pkill -f "uvicorn" || true
	pkill -f "vite" || true
	pkill -f "npm run dev" || true
	$(MAKE) delete_ci_artifacts
	
dev-restart-docker-compose: ## Restart docker compose for dev
	@echo "Restarting docker compose"
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH)  docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) down -v
	pkill -f "uvicorn" || true
	pkill -f "vite" || true
	pkill -f "npm run dev" || true
	docker volume prune -f
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) up --build 
dev-destroy-infra: ## Destroy terraform infra for development environmnet
	$(MAKE) check_enviroment_variables
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	$(MAKE) -C infra terraform-stop 



deploy-start: ## ups infra for prod and stagin
	$(MAKE) check_enviroment_variables
	$(MAKE) -C infra terraform-apply ENVIRONMENT=$(ENVIRONMENT)
	$(MAKE) -C infra sync_all ENVIRONMENT=$(ENVIRONMENT)
	$(MAKE) -C frontend build
	$(MAKE) -C backend push_docker
	$(MAKE) -C infra ansible-start

deploy-stop: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	$(MAKE) check_enviroment_variables
	$(MAKE) -C infra terraform-stop ENVIRONMENT="$(ENVIRONMENT)" 
	$(MAKE) delete_ci_artifacts

delete_ci_artifacts:
	rm -rf $(BACKEND_ENV_FILE_SYNCED_PATH)
	rm -rf $(FROTNEND_ENV_FILE_SYNCED_PATH)
	docker volume prune -f


container_names:
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) ps
container_logs:
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) logs $(SERVICE_NAME) -f

container_build:
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE_SYNCED_PATH) docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) up --build $(SERVICE_NAME) 

check_enviroment_variables:
	@if [ -z "$$ENVIRONMENT" ]; then \
		echo "Error: ENVIRONMENT must be defined"; \
		exit 1; \
	fi
	echo "Environment is: $(ENVIRONMENT)"