# Feature: Terraform Infrastructure Integration

## 1. Overview
**Summary**: Integrate Terraform to provision the underlying infrastructure for Nebulus.
**Goal**: Enable "Infrastructure as Code" (IaC) for reproducible deployments on GCP (and potentially other providers).
**Scope**:
- Create `terraform/` directory.
- Define `main.tf` for GCP VM provisioning.
- Use `variables.tf` for configuration.
- output public IP for Ansible consumption.

## 2. Requirements
- **Functional**:
    - Must provision a VM suitable for AI workloads (e.g., n1-standard-4 or similar).
    - Must allow HTTP/HTTPS and custom ports (3000, 8000, 8001, 8002, 11435).
    - Must perform SSH key injection.
- **Technical**:
    - Local state (for now) or GCS backend.
    - Terraform >= 1.0.0.

## 3. Implementation Plan
- [ ] Scaffold `terraform/` directory.
- [ ] Create `main.tf`, `variables.tf`, `outputs.tf`.
- [ ] Create `terraform.tfvars.example`.
- [ ] Verify `terraform init`.

## 4. Verification
- Run `terraform validate`.
- (Optional) `terraform plan` if credentials available.

## 5. Security Implications
- Use `.gitignore` to prevent committing `terraform.tfstate` and `.tfvars`.
