#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Nebulus Setup...${NC}"

# 1. Check for Docker (Crucial Prerequisite)
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed and is required.${NC}"
    echo "Please install Docker Desktop or Docker Engine + Compose plugin."
    exit 1
fi

# 2. Check/Install uv (Python Package Manager)
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Attempt to source cargo env for current session
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    else
        # Fallback to adding to PATH manually for this script execution
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
fi

# 3. Check/Install Ansible
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ansible not found. Installing via uv...${NC}"
    uv tool install ansible
    # Ensure uv tools are in PATH
    export PATH="$HOME/.local/bin:$PATH"
fi

# 4. Install Ansible Requirements
echo -e "${GREEN}📦 Installing Ansible collections...${NC}"
ansible-galaxy collection install community.docker

# 5. Run the Setup Playbook
echo -e "${GREEN}▶️  Executing Setup Playbook...${NC}"
# Determine script directory to resolve relative paths correctly
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
ansible-playbook -i ansible/inventory ansible/setup.yml

echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "   -----------------------------------------------------"
echo -e "   💻 Open WebUI:     http://localhost:3000"
echo -e "   🧠 MCP Server:     http://localhost:8000"
echo -e "   🦙 Ollama API:     http://localhost:11434"
echo -e "   -----------------------------------------------------"
