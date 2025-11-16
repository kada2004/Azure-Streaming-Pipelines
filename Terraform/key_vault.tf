resource "azurerm_key_vault" "streaming_time_SeriesIot" {
  name                       = "kv-${local.project_prefix}-TimeSeries"
  location                   = var.location
  resource_group_name        = azurerm_resource_group.rg.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days = 7
  purge_protection_enabled   = true

  sku_name = "standard"
  lifecycle {
    ignore_changes = [tags]
  }
}

# Function App access policy

resource "azurerm_key_vault_access_policy" "function_app01" {
  key_vault_id = azurerm_key_vault.streaming_time_SeriesIot.id
  tenant_id    = azurerm_linux_function_app.function_app_ingestion01.identity[0].tenant_id
  object_id    = azurerm_linux_function_app.function_app_ingestion01.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
}