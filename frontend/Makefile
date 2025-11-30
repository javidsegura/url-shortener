.PHONY: help install dev build build-local format

# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install frontend dependencies
	cd ./app && npm install

dev: ## Start frontend development server
	@echo "Starting frontend dev server"
	cd ./app && npm run dev

build: ## Build frontend based on ENVIRONMENT (production|staging)
	@if [ -z "$(ENVIRONMENT)" ]; then \
		echo "$(RED)Error: ENVIRONMENT required$(RESET)"; \
		exit 1; \
	fi
	cd ./app; \
	if [ "$(ENVIRONMENT)" = "production" ]; then \
		echo "$(GREEN)Building for production...$(RESET)"; \
		npm run build; \
	elif [ "$(ENVIRONMENT)" = "staging" ]; then \
		echo "$(GREEN)Building for staging...$(RESET)"; \
		npm run staging; \
	else \
		echo "$(RED)ENVIRONMENT must be 'production' or 'staging'$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Frontend build complete$(RESET)"

build-local: ## Build and preview frontend locally
	cd ./app; \
	npm run build; \
	npm run preview

format: ## Format frontend code using Prettier
	cd ./app && npm run format