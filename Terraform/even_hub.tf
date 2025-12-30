# Even Hub https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/eventhub.html

resource "azurerm_eventhub_namespace" "streaming_timeseries" {
  name                = "Iot-time-series"
  location            = var.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard"
  capacity            = 1

  tags = {
    Owner = "Iot-and-Weather"
  }
}

resource "azurerm_eventhub" "streaming01" {
  name              = "streaming_iot_time_series"
  namespace_id      = azurerm_eventhub_namespace.streaming_timeseries.id
  partition_count   = 3
  message_retention = 2
}

# Even Hub Consumer
resource "azurerm_eventhub_consumer_group" "asa_cg" {
  name                = "cg-stream-analytics"
  namespace_name      = azurerm_eventhub_namespace.streaming_timeseries.name
  eventhub_name       = azurerm_eventhub.streaming01.name
  resource_group_name = azurerm_resource_group.rg.name
}


