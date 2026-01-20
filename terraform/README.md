# Multi-Cloud Infrastructure

This directory contains Terraform configurations for deploying Nebulus to various cloud providers.

## Structure
- `gcp/`: Google Cloud Platform (Compute Engine)
- `aws/`: Amazon Web Services (EC2)
- `azure/`: Microsoft Azure (Virtual Machine)

## Usage
Navigate to the directory of your chosen provider and follow the standard Terraform workflow:

```bash
cd terraform/aws
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform init
terraform apply
```
