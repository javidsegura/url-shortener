# ========================================
# BLOB STORAGE (Azure's S3)
# ========================================
output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = module.blob_storage.storage_account_name
}

output "storage_container_name" {
  description = "Name of the blob container for images"
  value       = module.blob_storage.storage_container_name
}


# ========================================
# MYSQL DATABASE
# ========================================
output "mysql_host" {
  description = "Fully qualified domain name of the MySQL server"
  value       = module.mysql_db.database_fqdn
}

output "key_vault_db_secret_name" {
  description = "Name of the Key Vault secret containing DB credentials"
  value       = module.mysql_db.db_credentials_secret_name
}


# ========================================
# VIRTUAL MACHINE
# ========================================
output "vm_public_ip" {
  description = "Public IP address of the web application VM"
  value       = module.vm.vm_public_ip
}

output "vm_private_ip" {
  description = "Private IP address of the VM"
  value       = module.vm.vm_private_ip
}

output "vm_ssh_user" {
  description = "SSH username for the VM"
  value       = "azureuser"
}

output "vm_ssh_private_key_path" {
  description = "Path to the SSH private key file"
  value       = abspath(pathexpand(var.ssh_key_local_path))
}

output "vm_id" {
  description = "Resource ID of the virtual machine"
  value       = module.vm.vm_id
}


# ========================================
# GENERAL
# ========================================
output "azure_location" {
  description = "Azure region where resources are deployed"
  value       = var.location
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = var.resource_group_name
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}