# Function app1
#https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/function_app
resource "azurerm_app_service_plan" "Ingestion01" {
  name                = "azure-functions-Ingestion01-plan"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku {
    tier = "Standard"
    size = "S1"
  }
}

resource "azurerm_function_app" "function_app_ingestion01" {
  name                       = "Ingestion-azure-functions"
  location                   = var.location
  resource_group_name        = azurerm_resource_group.rg.name
  app_service_plan_id        = azurerm_app_service_plan.Ingestion01.id
  storage_account_name       = azurerm_storage_account.tfstate.name
  storage_account_access_key = azurerm_storage_account.tfstate.primary_access_key

  functions_extension_version = "~4"
  site_config {
    linux_fx_version = "Python|3.10" # adjust for runtime
  }
}