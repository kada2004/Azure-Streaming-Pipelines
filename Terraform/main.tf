resource "azurerm_resource_group" "rg" {
  name     = "rg-${local.project_prefix}-${local.project_name}"
  location = var.location

  lifecycle {
    ignore_changes = [tags]
  }
}