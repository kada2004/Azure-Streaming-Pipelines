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

