variable "location" {
  description = "Azure Region"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "nebulus-rg"
}

variable "vm_size" {
  description = "VM Size"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "admin_username" {
  description = "Admin username"
  type        = string
  default     = "nebulusadmin"
}

variable "ssh_public_key_path" {
  description = "Path to public SSH key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
