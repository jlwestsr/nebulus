#!/bin/bash

# Health Check Script
# Verifies the status of core services (Ollama, ChromaDB, MCP Server, WebUI)

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Checking Nebulus Health..."

# 1. Ollama
echo -n "Ollama (11435): "
if curl -s -f "http://localhost:11435/api/tags" > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# 2. ChromaDB
echo -n "ChromaDB (8001): "
if curl -s -f "http://localhost:8001/api/v2/heartbeat" > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    # Try getting logs if fail
    # docker logs blackbox-chromadb | tail -n 5
    exit 1
fi

# 3. MCP Server
echo -n "MCP Server (8000): "
if curl -s -f "http://localhost:8000/health" > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

# 4. Gantry (Chainlit)
echo -n "Gantry (8002): "
if curl -s -f -I "http://localhost:8002" > /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAIL${NC}"
    exit 1
fi

echo -e "\n${GREEN}All Systems Operational!${NC}"
exit 0
