resource "azurerm_service_plan" "streamlit_plan" {
  name                = "asp-streamlit"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  os_type             = "Linux"
  sku_name            = "P1v2"
}

resource "azurerm_linux_web_app" "streamlit_app" {
  name                = "streamlit-timeseries-12345"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  service_plan_id     = azurerm_service_plan.streamlit_plan.id

  https_only = true

  site_config {
    always_on = true

    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"

    #Run Streamlit on Azure-required port
    "STARTUP_COMMAND" = "streamlit run app.py --server.port 8000 --server.address 0.0.0.0"
  }
}
