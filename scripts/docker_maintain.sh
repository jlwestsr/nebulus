#!/bin/bash
# Docker Maintenance Script for Nebulus
#
# Purpose: Prevents disk bloat and daemon CPU spikes by pruning unused Docker resources.
# Usage: ./scripts/docker_maintain.sh

set -e

echo "=========================================="
echo "Nebulus Docker Maintenance"
echo "Date: $(date)"
echo "=========================================="

# 1. Prune Dangling Images
# These are the intermediate layers that often cause "snapshotter" issues if corrupted.
echo "[1/3] Pruning dangling images..."
docker image prune -f

# 2. Prune Builder Cache
# We keep cache younger than 48h to avoid slowing down active development.
echo "[2/3] Pruning builder cache (older than 48h)..."
docker builder prune -f --filter "until=48h"

# 3. Report Status
echo "[3/3] Current System Usage:"
docker system df

echo "=========================================="
echo "Maintenance Complete."
