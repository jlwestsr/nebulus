variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "machine_type" {
  description = "Compute Instance Machine Type"
  type        = string
  default     = "n1-standard-4"
}

variable "instance_name" {
  description = "Name of the Nebulus instance"
  type        = string
  default     = "nebulus-lab"
}

variable "source_ranges" {
  description = "Allowed source IP ranges for firewall"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "ssh_user" {
  description = "SSH Username"
  type        = string
  default     = "admin"
}

variable "ssh_pub_key_path" {
  description = "Path to public SSH key"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}
