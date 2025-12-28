# https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/postgresql_server.html

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "postgres" {
  name                = "azpostgresflexible"
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.location

  administrator_login    = "psqladmin"
  administrator_password = var.postgres_admin_password

  version    = "14"
  sku_name   = "GP_Standard_D4s_v3"
  storage_mb = 32768

  backup_retention_days = 7

  public_network_access_enabled = true
}


# Allow TimescaleDB extension on the server
resource "azurerm_postgresql_flexible_server_configuration" "enable_extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  value     = "timescaledb"
}

# Create database
resource "azurerm_postgresql_flexible_server_database" "timeseries_db" {
  name      = "timeseriesdb"
  server_id = azurerm_postgresql_flexible_server.postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Firewall rule – allow your public IP
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_my_ip" {
  name      = "allow-my-ip"
  server_id = azurerm_postgresql_flexible_server.postgres.id

  start_ip_address = "85.221.134.38"
  end_ip_address   = "85.221.134.38"
}
# Firewall rule – allow Azure services
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_azure" {
  name      = "AllowAzureServices"
  server_id = azurerm_postgresql_flexible_server.postgres.id

  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}
