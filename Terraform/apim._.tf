#https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/api_management
resource "azurerm_api_management" "apim_azure_stream" {
  name                = "apim-${local.project_prefix}-management"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name

  publisher_name  = "streaming-data-pipelines"
  publisher_email = "azurestreamingpipelines@gmail.com"

  sku_name = "Developer_1"

  identity {
    type = "SystemAssigned"
  }
}

# Gateway Method
resource "azurerm_api_management_api" "ingest" {
  name                = "ingest-api"
  resource_group_name = azurerm_resource_group.rg.name
  api_management_name = azurerm_api_management.apim_azure_stream.name

  revision     = "1"
  display_name = "Event Ingest API"
  path         = "ingest"
  protocols    = ["https"]


  service_url = "https://localhost"

  subscription_required = true
}

# Operation 
resource "azurerm_api_management_api_operation" "post_ingest" {
  operation_id        = "post-ingest"
  api_name            = azurerm_api_management_api.ingest.name
  api_management_name = azurerm_api_management.apim_azure_stream.name
  resource_group_name = azurerm_resource_group.rg.name

  display_name = "Post Ingest"
  method       = "POST"
  url_template = "/"
}

# Iam sender to even Hub 
resource "azurerm_eventhub_authorization_rule" "apim_sender" {
  name                = "apim-sender"
  namespace_name      = azurerm_eventhub_namespace.streaming_timeseries.name
  eventhub_name       = azurerm_eventhub.streaming01.name
  resource_group_name = azurerm_resource_group.rg.name

  send = true
}


# APIM Event Hub Logger
resource "azurerm_api_management_logger" "eventhub_logger" {
  name                = "eventhub-logger"
  api_management_name = azurerm_api_management.apim_azure_stream.name
  resource_group_name = azurerm_resource_group.rg.name

  eventhub {
    name              = azurerm_eventhub.streaming01.name
    connection_string = azurerm_eventhub_authorization_rule.apim_sender.primary_connection_string
  }
}

# Send data to even_hub
resource "azurerm_api_management_api_policy" "ingest_policy" {
  api_name            = azurerm_api_management_api.ingest.name
  api_management_name = azurerm_api_management.apim_azure_stream.name
  resource_group_name = azurerm_resource_group.rg.name

  xml_content = <<POLICY
<policies>
  <inbound>
    <base />

    <!-- Read body  -->
    <set-variable name="payload"
      value="@((string)context.Request.Body.As<string>(true))" />

    <!-- Log payload to Event Hub  -->
    <log-to-eventhub logger-id="eventhub-logger">
      @((string)context.Variables["payload"])
    </log-to-eventhub>

    <!-- Return immediately -->
    <return-response>
      <set-status code="202" reason="Accepted" />
      <set-header name="Content-Type" exists-action="override">
        <value>application/json</value>
      </set-header>
      <set-body>{"status":"accepted"}</set-body>
    </return-response>

  </inbound>

  <backend>
    <base />
  </backend>

  <outbound>
    <base />
  </outbound>

  <on-error>
    <base />
  </on-error>
</policies>
POLICY
}







