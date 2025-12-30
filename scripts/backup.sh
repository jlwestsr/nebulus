#!/bin/bash

# Automated Backup Script
# Backs up persistent Docker volumes for Ollama, ChromaDB, and Open WebUI.

set -e

BACKUP_DIR="$(pwd)/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VOLUMES=("nebulus_ollama_data" "nebulus_chroma_data" "nebulus_webui_data")

GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo "Starting backup process at $TIMESTAMP..."

for vol in "${VOLUMES[@]}"; do
    echo -n "Backing up $vol... "

    # Run a temporary alpine container to tar the volume content
    # We cd into /data so the tarball contains relative paths (cleaner restore)
    docker run --rm \
        -v "$vol":/data \
        -v "$BACKUP_DIR":/backup \
        alpine sh -c "cd /data && tar czf /backup/${vol}_${TIMESTAMP}.tar.gz ." || { echo "Failed!"; exit 1; }

    echo -e "${GREEN}Done${NC} -> backups/${vol}_${TIMESTAMP}.tar.gz"
done

# Cleanup old backups (retention policy: 30 days)
echo
echo "Checking for backups older than 30 days..."
find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +30 -print -exec rm {} \;

echo -e "\n${GREEN}Backup process completed successfully!${NC}"
