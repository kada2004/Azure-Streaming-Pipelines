terraform {
  backend "azurerm" {
    resource_group_name  = "rg-Az-Streaming_Pipelines"
    storage_account_name = "stazstreamtfstate"
    container_name       = "terraform-state"
    key                  = "terraform.tfstate"
  }
}