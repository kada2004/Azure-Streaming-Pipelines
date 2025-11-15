# Terraform backend storage
resource "azurerm_storage_account" "tfstate" {
  name                     = "stazstreamtfstate2"  
  resource_group_name      = "rg-Az-Streaming_Pipelines"
  location                 = "westeurope"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "terraform-state"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}