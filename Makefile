.PHONY: help dev install
.DEFAULT_GOAL := help

# VARIABLES
# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

ENVIRONMENT ?= dev
BACKEND_ENV_FILE = ./backend/.env.$(ENVIRONMENT)
TERRAFORM_PATH = ./infra/terraform/environment/$(ENVIRONMENT)
PROJECT_NAME = url-shortener


help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install project-wide dependencies
	@echo "$(YELLOW)Installing all project dependencies...$(RESET)"
	$(MAKE) -C backend install
	$(MAKE) -C frontend install
	$(MAKE) -C infra install
	brew install jq

dev-start: ## Hot reload enabled
	$(MAKE) -C infra up ENVIRONMENT=dev
	$(MAKE) -C infra sync_envs
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE).synced docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) up --build &
	$(MAKE) -C frontend dev &
	$(MAKE) container_logs SERVICE_NAME=backend

dev-stop: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE).synced  docker compose -f docker-compose.yml -f docker-compose.dev.yml -p $(PROJECT_NAME) down 
	pkill -f "uvicorn" || true
	pkill -f "vite" || true
	pkill -f "npm run dev" || true
	$(MAKE) delete_ci_artifacts

prod-start: ## ups infra for prod and stagin
	$(MAKE) -C infra up ENVIRONMENT=$(ENVIRONMENT)
	$(MAKE) -C infra sync_all ENVIRONMENT=$(ENVIRONMENT)
	$(MAKE) -C frontend build
	$(MAKE) -C backend push_docker
	$(MAKE) -C infra ansible-up

prod-stop: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	$(MAKE) -C infra down ENVIRONMENT="$(ENVIRONMENT)" 
	$(MAKE) delete_ci_artifacts

start-full-containerization: ## Containiizes backend, builts frontend -- essentially, dev with no hot-reload
	$(MAKE) -C infra up ENVIRONMENT=$(ENVIRONMENT)
	$(MAKE) -C infra sync_all ENVIRONMENT=$(ENVIRONMENT)
	$(MAKE) -C frontend build
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE).synced docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) up
	$(MAKE) -C infra ansible-up

stop-full-containerization: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	$(MAKE) -C infra down ENVIRONMENT="$(ENVIRONMENT)" 
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE).synced docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) down
	$(MAKE) delete_ci_artifacts

delete_ci_artifacts:
	rm -rf $(BACKEND_ENV_FILE).synced

container_logs:
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE).synced docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) logs $(SERVICE_NAME) -f

container_build:
	BACKEND_ENV_FILE=$(BACKEND_ENV_FILE).synced docker compose -f docker-compose.yml -f docker-compose.prod.yml -p $(PROJECT_NAME) up --build $(SERVICE_NAME) 
