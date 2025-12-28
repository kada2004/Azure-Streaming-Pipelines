#https://registry.terraform.io/providers/hashicorp/azurerm/4.2.0/docs/resources/synapse_workspace
resource "azurerm_synapse_workspace" "synapse" {
  name                                 = "spazworksapce"
  resource_group_name                  = azurerm_resource_group.rg.name
  location                             = var.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.synapse.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = var.synapse_sql_password

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_synapse_firewall_rule" "allow_all" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}
# dedicated sql pool to synapse
resource "azurerm_synapse_sql_pool" "dedicated_pool" {
  name                      = "sqlpoolaz"
  synapse_workspace_id      = azurerm_synapse_workspace.synapse.id
  sku_name                  = "DW100c"
  create_mode               = "Default"
  storage_account_type      = "LRS"
  geo_backup_policy_enabled = false
  lifecycle {
    ignore_changes = [
      storage_account_type
    ]
  }
}
