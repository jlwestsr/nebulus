#!/bin/bash
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Quality Assurance Checks...${NC}"

# Check if running in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        echo "Activating virtual environment..."
        source .venv/bin/activate
    else
        echo -e "${RED}Warning: No virtual environment detected and .venv not found.${NC}"
    fi
fi

# Run Flake8
echo -e "\n${GREEN}Running Flake8 Linting...${NC}"
if flake8 .; then
    echo -e "${GREEN}Flake8 checks passed.${NC}"
else
    echo -e "${RED}Flake8 checks failed.${NC}"
    exit 1
fi

# Run Pytest
echo -e "\n${GREEN}Running Pytest...${NC}"
if pytest -p no:cacheprovider; then
    echo -e "${GREEN}All tests passed.${NC}"
else
    echo -e "${RED}Tests failed.${NC}"
    exit 1
fi

echo -e "\n${GREEN}All checks passed successfully!${NC}"
