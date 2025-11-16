# Azure VM Module - Key Concepts & Parameters

## Overview
This module creates an Azure Linux VM with secure access to Blob Storage and Key Vault, equivalent to the AWS EC2 setup.

---

## 🔑 Key Azure Concepts

### 1. **Managed Identity** (Azure's IAM Role)
```hcl
resource "azurerm_user_assigned_identity" "vm_identity"
```
- **What it is**: Azure's equivalent to AWS IAM Instance Profile
- **Why**: Allows the VM to authenticate to Azure services without storing credentials
- **How it works**: The VM gets a token from Azure's metadata service to access resources

### 2. **Network Interface (NIC)**
```hcl
resource "azurerm_network_interface" "vm_nic"
```
- **What it is**: Virtual network card for the VM
- **Why needed**: Azure VMs require an explicit NIC resource (AWS abstracts this)
- **Key settings**:
  - `private_ip_address_allocation = "Dynamic"` - Azure DHCP assigns IP
  - Links subnet, public IP, and VM together

### 3. **Public IP Resource**
```hcl
allocation_method = "Static"
sku = "Standard"
```
- **Static**: IP won't change on VM restart (required for DNS)
- **Standard SKU**: Required for zone-redundant resources and Standard Load Balancer

---

## 🔐 Security & Networking

### Application Security Group (ASG) Association
```hcl
resource "azurerm_network_interface_application_security_group_association"
```
- **Purpose**: Tags this VM's NIC with the "web-app" ASG
- **Why**: Database NSG uses this to allow MySQL traffic from web tier
- **AWS equivalent**: Security group references (e.g., `security_groups = [sg-xxx]`)

### NSG Association
```hcl
resource "azurerm_network_interface_security_group_association"
```
- **Purpose**: Applies firewall rules to this VM's NIC
- **Rules applied**: HTTP (80), HTTPS (443), SSH (22)

---

## 💻 VM Configuration

### VM Size
```hcl
size = "Standard_B2s"
```
- **Specs**: 2 vCPUs, 4GB RAM
- **AWS equivalent**: `t3.small`
- **B-series**: Burstable VMs for workloads that don't need full CPU constantly

### OS Disk
```hcl
os_disk {
  caching = "ReadWrite"
  storage_account_type = "Standard_LRS"
  disk_size_gb = 30
}
```
- **`caching = "ReadWrite"`**: Host-level caching for better performance
- **`Standard_LRS`**: Locally Redundant Storage (3 copies within one datacenter)
- **Alternatives**: 
  - `Premium_LRS` - SSD (faster, more expensive)
  - `StandardSSD_LRS` - SSD at Standard pricing

### Image
```hcl
source_image_reference {
  publisher = "Canonical"
  offer     = "0001-com-ubuntu-server-jammy"
  sku       = "22_04-lts-gen2"
  version   = "latest"
}
```
- **Ubuntu 22.04 LTS**: Long-term support until 2027
- **Gen2**: Supports UEFI-based boot (better security, faster boot times)

### Identity Block
```hcl
identity {
  type = "UserAssigned"
  identity_ids = [azurerm_user_assigned_identity.vm_identity.id]
}
```
- **UserAssigned**: Identity exists independently of VM (can be reused)
- **Alternative**: `SystemAssigned` - tied to VM lifecycle, auto-deleted with VM

---

## 🔓 RBAC Permissions

### Blob Storage Access
```hcl
role_definition_name = "Storage Blob Data Contributor"
scope = var.storage_account_id
principal_id = azurerm_user_assigned_identity.vm_identity.principal_id
```
- **Role**: Read, write, delete blobs
- **Scope**: Entire storage account
- **principal_id**: The managed identity's Azure AD object ID

### Key Vault Access
```hcl
role_definition_name = "Key Vault Secrets User"
scope = var.key_vault_id
```
- **Role**: Read secret values only (not manage secrets)
- **Alternative**: `Key Vault Secrets Officer` - can create/delete secrets

---

## 🆚 AWS vs Azure Comparison

| AWS | Azure | Notes |
|-----|-------|-------|
| IAM Instance Profile | Managed Identity | Azure's approach is simpler |
| Security Group on instance | NSG on NIC | NSG must be explicitly associated |
| SG-to-SG references | ASG membership | Azure uses ASG tags for this |
| IAM Policy attachments | RBAC role assignments | Azure uses built-in roles |
| S3 bucket policy | Storage account RBAC | No need for complex JSON policies |
| Secrets Manager | Key Vault | Similar purpose, different API |

---

## 📋 Required Variables

| Variable | Purpose |
|----------|---------|
| `storage_account_id` | From blob_storage module - for RBAC scope |
| `key_vault_id` | From mysql_db module - for RBAC scope |
| `web_app_asg_id` | From VPC module - to tag VM for DB access |
| `web_app_nsg_id` | From VPC module - firewall rules |
| `public_subnet_id` | From VPC module - where to place VM |

---

## 🔄 Authentication Flow

1. **VM boots** with managed identity attached
2. **App needs blob access**:
   - App calls Azure Instance Metadata Service (IMDS) at `http://169.254.169.254`
   - Gets OAuth token for Storage
   - Uses token to authenticate to Blob Storage
3. **App needs database credentials**:
   - App calls IMDS for Key Vault token
   - Uses token to read secret from Key Vault
   - Parses JSON to get DB username/password

**Key advantage**: No credentials stored on disk or in environment variables!

