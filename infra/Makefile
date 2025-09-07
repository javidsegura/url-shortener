.PHONY: help install up down output

# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

.DEFAULT_GOAL := help

ENVIRONMENT ?= dev
BACKEND_ENV_FILE = ../backend/.env.$(ENVIRONMENT)
FRONTEND_ENV_FILE = ../frontend/app/.env.$(ENVIRONMENT)
ANSIBLE_INVENTORY_FILE = ./ansible/inventory/$(ENVIRONMENT).ini
TERRAFORM_PATH=terraform/environment/$(ENVIRONMENT)
SYNC_SCRIPT_PATH = ../scripts/sync_terraform_outputs.py

help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Initialize Terraform
	cd $(TERRAFORM_PATH) && terraform init
	brew install ansible
	ansible-galaxy collection install community.docker

up: ## Apply Terraform configuration
	@echo "Environment is $(ENVIRONMENT)"
	cd $(TERRAFORM_PATH) && terraform apply

down: ## Apply Terraform configuration
	@echo "Environment is $(ENVIRONMENT)"
	cd $(TERRAFORM_PATH) && terraform destroy

output:
	cd $(TERRAFORM_PATH) && terraform output -json

ansible-ping:
	ansible all -m ping -i ./ansible/inventory/$(ENVIRONMENT).ini

ansible-up:
	ansible-playbook ./ansible/playbook/multi-container.yml -i ./ansible/inventory/$(ENVIRONMENT).ini 

sync_backend_env: 
	@echo "Syncing Terraform outputs to backend .env..."
	cp $(BACKEND_ENV_FILE) $(BACKEND_ENV_FILE).synced
	python3 $(SYNC_SCRIPT_PATH) \
	   --terraform-path $(TERRAFORM_PATH) \
	   --environment $(ENVIRONMENT) \
	   --backend-env $(BACKEND_ENV_FILE).synced \
	   --backend-prefixes api_ backend_

sync_frontend_env:
	@echo "Syncing Terraform outputs to Ansible inventory..."
	python3 $(SYNC_SCRIPT_PATH) \
		--terraform-path $(TERRAFORM_PATH) \
		--environment $(ENVIRONMENT) \
		--frontend-env $(FRONTEND_ENV_FILE).synced \
		--frontend-prefixes server_ frontend_

sync_ansible_inventory:
	@echo "Syncing Terraform outputs to Ansible inventory..."
	python3 $(SYNC_SCRIPT_PATH) \
		--terraform-path $(TERRAFORM_PATH) \
		--environment $(ENVIRONMENT) \
		--ansible-inventory $(ANSIBLE_INVENTORY_FILE) \
		--ansible-prefixes ssh_ server_ ansible_


sync_envs:
	$(MAKE) sync_backend_env
	$(MAKE) sync_frontend_env

sync_all:
	$(MAKE) sync_envs
	$(MAKE) sync_ansible_inventory


