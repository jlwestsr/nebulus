#!/bin/bash

# Restore Script
# Restores a specific backup file to a Docker volume.

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <backup_file_name> <volume_name>"
    echo "Example: $0 nebulus_webui_data_20240101.tar.gz nebulus_webui_data"
    exit 1
fi

BACKUP_FILE=$1
VOLUME=$2
BACKUP_DIR="$(pwd)/backups"

# Check if backup file exists
if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file '$BACKUP_DIR/$BACKUP_FILE' not found.${NC}"
    exit 1
fi

echo -e "${YELLOW}WARNING: This will OVERWRITE all data in volume '$VOLUME'.${NC}"
echo -e "${YELLOW}It is recommended to stop containers using this volume first.${NC}"
read -p "Are you sure you want to proceed? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 1
fi

echo -n "Restoring '$BACKUP_FILE' to '$VOLUME'... "

# Restore process:
# 1. Mount volume and backup dir
# 2. Clean existing data in volume (rm -rf *)
# 3. Extract tarball
docker run --rm \
    -v "$VOLUME":/data \
    -v "$BACKUP_DIR":/backup \
    alpine sh -c "cd /data && rm -rf * && tar xzf /backup/$BACKUP_FILE" || { echo "Failed!"; exit 1; }

echo -e "${GREEN}Done!${NC}"
