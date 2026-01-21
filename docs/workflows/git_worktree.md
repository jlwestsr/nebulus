# Git Worktree Workflow

This workflow allows multiple AI agents or developers to work on the same repository simultaneously in parallel directories, without conflicting with each other's file states.

## Concept

Instead of cloning the repo multiple times (which wastes disk space and requires managing multiple remotes), we use `git worktree`.
This allows us to have a "main" repository and multiple "linked" working directories, each checked out to a different branch.

## Directory Structure

We recommend the following sibling directory structure to avoid nesting worktrees inside the main repo:

```text
projects/west_ai_labs/
├── nebulus/                 # Main Repo (bare or standard)
├── nebulus-worktrees/       # Directory to hold worktrees
│   ├── feat-login-ui/       # Worktree for 'feat/login-ui' branch
│   └── fix-docker-crash/    # Worktree for 'fix/docker-crash' branch
```

## How to Create a Worktree

We provide a helper script to automate setup and ensure the `.venv` is correctly linked.

### Usage

```bash
./scripts/create_worktree.sh <branch_name> <target_directory>
```

### Example

```bash
# Create a worktree for a new feature
./scripts/create_worktree.sh feat/new-dashboard ../nebulus-worktrees/feat-new-dashboard
```

### What the script does

1. Creates a new worktree at the specified directory.
2. checks out the specified branch.
3. **Symlinks the `.venv`** from the main repo to the new worktree (Saving ~1.2GB).
4. Copies `.env` from the main repo (if it exists).

## Critical Rules

1. **Do NOT run `git worktree prune` inside the main repo** while worktrees are active, unless you intend to disconnect them.
2. **Shared Venv**: By default, all worktrees share the same libraries.
    - **Pros**: Fast setup, zero disk usage.
    - **Cons**: Upgrading a library in one worktree upgrades it for ALL.
    - **Fix**: If you need isolation, delete the `.venv` symlink in your worktree and run `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
