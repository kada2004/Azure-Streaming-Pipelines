# Create a Storage Account for Terraform backend
resource "azurerm_storage_account" "tfstate" {
  name = lower(replace("st${local.project_prefix}${local.project_name}tfstate", "_", ""))
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  tags = {
    Environment = "Terraform"
    Project     = local.project_name
  }
}

# Create a Blob Container for Terraform state
resource "azurerm_storage_container" "tfstate" {
  name                  = "terraform_state"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}