# Development Workflow

## Conventional Commits

Use the following prefixes for all commit messages:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `chore:` — Maintenance (configs, dependencies, gitignore)

## Python Environment

**MANDATORY**: Use the project's local virtual environment (`venv/`). Do NOT use global system packages or other environments. Activate immediately:

```bash
source venv/bin/activate
```

## Git Tracking & Branching

- **NO DIRECT WORK ON MAIN/MASTER**. This branch is for production releases only.
- **Local Branch Policy**: `feat/`, `fix/`, `docs/`, and `chore/` branches are **LOCAL ONLY**. Never push them to origin. Only `develop` and `main` are allowed on the remote.
- **Push Authorization**: All pushes to `origin` require explicit, just-in-time user approval.
- Always merge `develop` into your feature branch before requesting a merge back.

## Parallel Development (Git Worktree)

For parallel development (e.g., running multiple AI agents simultaneously), use `git worktree` instead of cloning the repository multiple times.

- **Mandatory Script**: Use `scripts/create_worktree.sh <branch> <path>` to set up new worktrees. This script automatically symlinks the main `venv` for zero disk overhead.
- **Forbidden**: Do NOT manually run `git worktree add` unless you explicitly intend to create a separate virtual environment.
- **Directory Structure**: Create worktrees in a sibling directory (e.g., `../nebulus-worktrees/`).
- **Cleanup**: Remove worktrees using `git worktree remove <path>` when finished. NEVER run `git worktree prune` inside the main repo while active worktrees exist.

## Workflows by Commit Type

### Feature (`feat`)

1. Create `docs/features/name.md` from template.
2. `git checkout -b feat/feature-name`
3. Implement changes.
4. Run `scripts/run_tests.sh`.
5. `git checkout develop && git merge feat/feature-name`
6. Ask for permission, then `git push origin develop`.

### Bug Fix (`fix`)

1. Reproduce the bug with a failing test/script.
2. `git checkout -b fix/issue-description`
3. Implement fix.
4. Pass reproduction script AND `scripts/run_tests.sh`.
5. `git checkout develop && git merge fix/issue-description`
6. Ask for permission, then `git push origin develop`.

### Documentation (`docs`)

1. `git checkout -b docs/description`
2. Update `README.md`, `docs/`, or other artifacts.
3. Check rendering and links.
4. `git checkout develop && git merge docs/description`
5. Ask for permission, then `git push origin develop`.

### Maintenance (`chore`)

1. `git checkout -b chore/description`
2. Update configs, dependencies, or gitignore.
3. Run `scripts/run_tests.sh`.
4. `git checkout develop && git merge chore/description`
5. Ask for permission, then `git push origin develop`.

## Verification

### Before Pushing

```bash
# Full pre-commit suite
pre-commit run --all-files

# Or use the project script
./scripts/run_tests.sh
```

### After Ansible Changes

```bash
ansible-playbook ansible/verify.yml
```

### Node.js

Use `community.general.npm` with `global: true` for system-wide CLI tools. Ensure `nodejs` and `npm` are installed via `apt` in the `common` role first.

## Security

- Never commit `~/.ssh/` keys or personal tokens.
- If a script needs to check for them, it should do so without exposing contents.
