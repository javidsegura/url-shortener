.PHONY: help install up down output

# Colors for output
RED = \033[31m
GREEN = \033[32m
YELLOW = \033[33m
BLUE = \033[34m
RESET = \033[0m

.DEFAULT_GOAL := help

BASE_BACKEND_ENV_FILE_PATH = ../backend/env_config/base/.env.$(ENVIRONMENT)
BASE_FRONTEND_ENV_FILE_PATH = ../frontend/app/env_config/base/.env.$(ENVIRONMENT)
ANSIBLE_INVENTORY_FILE_PATH = ./ansible/inventory/$(ENVIRONMENT).ini

TERRAFORM_ENVIRONMENT_PATH=terraform/environment/$(ENVIRONMENT)
TERRAFORM_SET_UP_PATH=terraform/set-up
SYNC_SCRIPT_PATH = scripts.main

help: ## Show this help message
	@echo "$(BLUE)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install-remote-state:
	cd $(TERRAFORM_SET_UP_PATH) && terraform init && terraform apply 
uninstall-remote-state:
	cd $(TERRAFORM_SET_UP_PATH) && terraform destroy

install: ## Initialize Terraform
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform init
	brew install ansible
	ansible-galaxy collection install community.docker

check: ## Apply Terraform configuration
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform plan

output:
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform output 
output-json:
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform output -json

terraform-start: ## Apply Terraform configuration
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform apply

terraform-stop: ## Apply Terraform configuration
	$(MAKE) check_enviroment_variables
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform destroy


ansible-ping: ## Check ansible connection is up
	$(MAKE) check_enviroment_variables
	ansible all -m ping -i ./ansible/inventory/$(ENVIRONMENT).ini

ansible-up:
	ansible-playbook ./ansible/playbook/multi-container.yml -i ./ansible/inventory/$(ENVIRONMENT).ini 

terraform-check:
	cd $(TERRAFORM_ENVIRONMENT_PATH) && terraform plan


sync_backend_env: ## Inject tf outputs into backend dotenv
	@echo "Syncing Terraform outputs to backend .env..."
	$(MAKE) check_enviroment_variables
	python3 -m $(SYNC_SCRIPT_PATH) \
	   --environment $(ENVIRONMENT) \
	   --terraform-dir $(TERRAFORM_ENVIRONMENT_PATH) \
	   --backend-dotenv-path $(BASE_BACKEND_ENV_FILE_PATH)

sync_frontend_env:  ## Inject tf outputs into frontend dotenv
	@echo "Syncing Terraform outputs to backend .env..."
	$(MAKE) check_enviroment_variables
	python3 -m $(SYNC_SCRIPT_PATH) \
	   --environment $(ENVIRONMENT) \
	   --terraform-dir $(TERRAFORM_ENVIRONMENT_PATH) \
	   --frontend-dotenv-path $(BASE_FRONTEND_ENV_FILE_PATH)


sync_ansible_inventory:
	@echo "Syncing Terraform outputs to Ansible inventory..."
	$(MAKE) check_enviroment_variables
	python3 -m $(SYNC_SCRIPT_PATH) \
	   --environment $(ENVIRONMENT) \
	   --terraform-dir $(TERRAFORM_ENVIRONMENT_PATH) \
	   --ansible-inventory-path $(ANSIBLE_INVENTORY_FILE_PATH)


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
