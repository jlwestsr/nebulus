#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Nebulus Bootstrap...${NC}"

# 1. Check for Python 3.12+
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    exit 1
fi

# 2. Setup Virtual Environment
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
VENV_DIR="$PROJECT_ROOT/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}📦 Creating virtual environment...${NC}"
    uv venv "$VENV_DIR"
else
    echo -e "${GREEN}✅ Virtual environment exists.${NC}"
fi

# 3. Install Dependencies
echo -e "${GREEN}📥 Installing dependencies...${NC}"
source "$VENV_DIR/bin/activate"
uv pip install -r "$PROJECT_ROOT/requirements.txt" -r "$PROJECT_ROOT/requirements-dev.txt" -r "$PROJECT_ROOT/src/mcp_server/requirements.txt"

# 4. Install Ansible (if not present)
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ansible not found in venv. Installing...${NC}"
    uv pip install ansible
    ansible-galaxy collection install community.docker
fi

# 5. Hand off to Ansible
echo -e "${GREEN}▶️  Handing off to Ansible...${NC}"
ansible-playbook -i "$PROJECT_ROOT/ansible/inventory" "$PROJECT_ROOT/ansible/setup.yml"

echo -e "${GREEN}✅ Bootstrap Complete!${NC}"
