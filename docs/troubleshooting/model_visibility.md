# Troubleshooting: Open WebUI Model Visibility

## Issue Description
Users reported observing duplicate model names in the Open WebUI dropdown menu: both the "Friendly Name" (e.g., "Llama 3.2 Vision") and the "Technical/Raw Name" (e.g., `llama3.2-vision:latest`) were visible simultaneously. This occurred despite configuring "Friendly Models" in the database.

## Root Causes

### 1. Environment Variable Parsing (Quoting)
The `MODEL_FILTER_LIST` environment variable in `docker-compose.yml` was encapsulated in single quotes:
```yaml
# Incorrect
MODEL_FILTER_LIST='llama-3.2-vision;llama-3.1;qwen-2.5-coder'
```
The Docker container environment treated the single quotes as *part of the string value*. Consequently, Open WebUI's filter logic failed to match the model IDs because it was looking for IDs starting or ending with a quote.

### 2. Database "Hidden" Models
We initially attempted to hide the raw models by inserting them into the `model` table with `is_active=0`.
However, explicitly registering a raw model ID (e.g., `llama3.2-vision:latest`) in the `model` table causes Open WebUI to treat it as a **Custom Model**. Even if inactive, it seemingly interfered with the dynamic model discovery filtering logic, or the system forced it to be available because it was explicitly defined.

### 3. Default Model Configuration
The `DEFAULT_MODELS` environment variable was set to the raw ID `llama3.2-vision:latest`. Open WebUI ensures the default model is always available in the list, potentially overriding filter settings.

### 4. Admin Access Control
By default, `BYPASS_ADMIN_ACCESS_CONTROL` is set to `true`. This grants administrators access to *all* models, bypassing the whitelist filter (`ENABLE_MODEL_FILTER`).

## Solution

### 1. Correct Environment Variables
We updated `docker-compose.yml` to remove quotes and ensure strict boolean formatting:
```yaml
# Correct
BYPASS_ADMIN_ACCESS_CONTROL=false
ENABLE_MODEL_FILTER=true
MODEL_FILTER_LIST=llama-3.2-vision;llama-3.1;qwen-2.5-coder
DEFAULT_MODELS=llama-3.2-vision
```

### 2. Database Cleanup
We modified the `scripts/configure_friendly_models.py` script to **delete** the raw model entries from the database instead of marking them as inactive. This removes them from the "Custom Model" registry, allowing the `ENABLE_MODEL_FILTER` whitelist to correctly filter the dynamically discovered Ollama models.

### 3. Friendly Default Model
We updated `DEFAULT_MODELS` to use the friendly ID (`llama-3.2-vision`), ensuring the default selection aligns with the whitelisted items.

## Verification
After applying these changes and recreating the container, only the friendly model names are visible in the dropdown for both admin and regular users.
