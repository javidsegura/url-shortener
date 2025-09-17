.PHONY: help install up down output

# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

.DEFAULT_GOAL := help

BACKEND_ENV_FILE_BASE_PATH = ../backend/.env.$(ENVIRONMENT).base
BACKEND_ENV_FILE_SYNCED_PATH = ../backend/.env.$(ENVIRONMENT).synced # CAN THIS BE DELETEED?
FRONTEND_ENV_FILE = ../frontend/app/.env.$(ENVIRONMENT) 
ANSIBLE_INVENTORY_FILE = ./ansible/inventory/$(ENVIRONMENT).ini
TERRAFORM_PATH=terraform/environment/$(ENVIRONMENT)
SYNC_SCRIPT_PATH = scripts.injector

help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Initialize Terraform
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_PATH) && terraform init
	brew install ansible
	ansible-galaxy collection install community.docker

check: ## Apply Terraform configuration
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_PATH) && terraform plan

output:
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_PATH) && terraform output 
output-json:
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_PATH) && terraform output -json

up: ## Apply Terraform configuration
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_PATH) && terraform apply

down: ## Apply Terraform configuration
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_PATH) && terraform destroy


ansible-ping:
	$(MAKE) check_enviroment_variables
	ansible all -m ping -i ./ansible/inventory/$(ENVIRONMENT).ini

ansible-up:
	ansible-playbook ./ansible/playbook/multi-container.yml -i ./ansible/inventory/$(ENVIRONMENT).ini 

terraform-check:
	cd $(TERRAFORM_PATH) && terraform plan


sync_backend_env: ## Inject tf outputs into backend dotenv
	@echo "Syncing Terraform outputs to backend .env..."
	$(MAKE) check_enviroment_variables
	python3 -m $(SYNC_SCRIPT_PATH) \
	   --environment $(ENVIRONMENT) \
	   --terraform-dir $(TERRAFORM_PATH) \
	   --base-dotenv-path $(BACKEND_ENV_FILE_BASE_PATH)

sync_frontend_env:
	@echo "Syncing Terraform outputs to Ansible inventory..."
	$(MAKE) check_enviroment_variables
	python3 $(SYNC_SCRIPT_PATH) \
		--terraform-path $(TERRAFORM_PATH) \
		--environment $(ENVIRONMENT) \
		--frontend-env $(FRONTEND_ENV_FILE).synced \
		--frontend-prefixes env_frontend_

sync_ansible_inventory:
	@echo "Syncing Terraform outputs to Ansible inventory..."
	$(MAKE) check_enviroment_variables
	python3 $(SYNC_SCRIPT_PATH) \
		--terraform-path $(TERRAFORM_PATH) \
		--environment $(ENVIRONMENT) \
		--ansible-inventory $(ANSIBLE_INVENTORY_FILE) \
		--ansible-prefixes ansible_


sync_envs:
	$(MAKE) sync_backend_env
	$(MAKE) sync_frontend_env

sync_all:
	$(MAKE) sync_envs
	$(MAKE) sync_ansible_inventory

check_enviroment_variables:
	@if [ -z "$$ENVIRONMENT" ]; then \
		echo "Error: ENVIRONMENT must be defined"; \
		exit 1; \
	fi
	echo "Environment is: $(ENVIRONMENT)"
