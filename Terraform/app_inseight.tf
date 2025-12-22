resource "azurerm_application_insights" "ingestion_ai" {
  name                = "appi-ingestion-azure-functions"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
}
