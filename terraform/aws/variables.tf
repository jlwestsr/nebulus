variable "region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 Instance Type"
  type        = string
  default     = "t3.xlarge"
}

variable "key_name" {
  description = "Name of existing AWS Key Pair"
  type        = string
}

variable "ami_id" {
  description = "AMI ID (default: Amazon Linux 2023)"
  type        = string
  default     = "ami-0230bd60aa48260c6" # Update per region!
}
