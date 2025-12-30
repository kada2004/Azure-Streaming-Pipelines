# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/stream_analytics_job.html
resource "azurerm_stream_analytics_job" "stream_analytics" {
  name                = "asa-${local.project_prefix}-${local.project_name}"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location
  identity {
    type = "SystemAssigned"
  }

  compatibility_level                      = "1.2"
  data_locale                              = "en-GB"
  events_late_arrival_max_delay_in_seconds = 60
  events_out_of_order_max_delay_in_seconds = 50
  events_out_of_order_policy               = "Adjust"
  output_error_policy                      = "Drop"
  streaming_units                          = 3
  sku_name                                 = "StandardV2"

  tags = {
    project = local.project_name
    env     = local.environment
  }

  transformation_query = <<QUERY
SELECT *
INTO [output-placeholder]
FROM [input-placeholder]
QUERY

  lifecycle {
    ignore_changes = [transformation_query]
  }
}

resource "azurerm_stream_analytics_stream_input_eventhub" "input_eventhub" {
  name                      = "inputEventHub"
  stream_analytics_job_name = azurerm_stream_analytics_job.stream_analytics.name
  resource_group_name       = azurerm_resource_group.rg.name

  servicebus_namespace = azurerm_eventhub_namespace.streaming_timeseries.name
  eventhub_name        = azurerm_eventhub.streaming01.name

  authentication_mode = "Msi"

  serialization {
    type     = "Json"
    encoding = "UTF8"
  }
}


