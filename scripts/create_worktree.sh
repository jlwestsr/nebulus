#!/bin/bash
# Helper script to create a git worktree with a shared .venv
# Usage: ./scripts/create_worktree.sh <branch_name> <directory_path>

set -e

BRANCH_NAME=$1
TARGET_DIR=$2
MAIN_REPO_DIR=$(pwd)

if [ -z "$BRANCH_NAME" ] || [ -z "$TARGET_DIR" ]; then
    echo "Usage: $0 <branch_name> <directory_path>"
    exit 1
fi

# 1. Create Worktree
echo "Creating worktree for '$BRANCH_NAME' at '$TARGET_DIR'..."
git worktree add -b "$BRANCH_NAME" "$TARGET_DIR"

# 2. Link .venv (Shared Strategy)
echo "Linking shared .venv..."
# Resolve absolute path for symlink validity
ABS_VENV_PATH="$MAIN_REPO_DIR/.venv"
ln -s "$ABS_VENV_PATH" "$TARGET_DIR/.venv"

# 3. Copy .env
if [ -f ".env" ]; then
    echo "Copying .env..."
    cp .env "$TARGET_DIR/.env"
fi

echo "=================================================="
echo "Worktree Ready!"
echo "Location: $TARGET_DIR"
echo "Branch:   $BRANCH_NAME"
echo "Venv:     Shared (Symlinked)"
echo "=================================================="
echo "To use:"
echo "  cd $TARGET_DIR"
echo "  source .venv/bin/activate"
