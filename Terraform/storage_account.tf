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

# Function app stg account
resource "azurerm_storage_account" "functionsa" {
  name                     = "stazstreamfunctionap01"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}

# Historical data / st account
resource "azurerm_storage_account" "historical_datastore" {
  name                     = "st${local.storage_name}${local.environment}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"

  is_hns_enabled = true
}

# Containers 
resource "azurerm_storage_container" "temperature" {
  name                  = "temperature"
  storage_account_name  = azurerm_storage_account.historical_datastore.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "iot_stream" {
  name                  = "iot-stream"
  storage_account_name  = azurerm_storage_account.historical_datastore.name
  container_access_type = "private"
}

resource "azurerm_storage_data_lake_gen2_filesystem" "synapse" {
  name               = "synapse"
  storage_account_id = azurerm_storage_account.historical_datastore.id
}

