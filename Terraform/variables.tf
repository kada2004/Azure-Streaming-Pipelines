variable "location" {
  type        = string
  description = "Name of the region"
  default     = "WestEurope"
}
variable "synapse_sql_password" {
  description = "Password for Synapse SQL admin"
  type        = string
  sensitive   = true
}

variable "postgres_admin_password" {
  description = "Password for Postgresql  admin"
  type        = string
  sensitive   = true
}