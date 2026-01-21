---
trigger: always_on
---

# AI Agent Behavior & Operational Rules

This document outlines the specific operational standards and behavioral expectations for AI agents working on this project.

## 0. Agent Configuration & Rule Hierarchy

When opening a project, the Google Antigravity IDE looks first for rules in the local workspace folder before falling back to global system-wide rules.

### Rule Locations

- **Workspace Rules**: The IDE first checks the project's local directory at `your-workspace/.agent/rules/`. It may also load configuration from files like `.cursorrules` or `.antigravity/rules.md` within the workspace root.
- **Global Rules**: If no workspace-specific rules are found, the IDE uses the global rule file at `~/.gemini/GEMINI.md`.

### Directory Structure & Use Cases

| Type | Default File Path | Use Case |
|------|-------------------|----------|
| **Workspace Rule** | `your-workspace/.agent/rules/` | Project-specific coding standards or restrictions. |
| **Global Rule** | `~/.gemini/GEMINI.md` | Universal behavior guidelines across all projects. |
| **Workspace Workflow** | `your-workspace/agent/workflows/` | On-demand tasks (e.g., `/generate-unit-tests`). |
| **Global Workflow** | `~/.gemini/antigravity/global_workflows/` | Reusable prompts available in every workspace. |

Rules control the autonomous agent's behavior. They can enforce coding styles or require documentation. The Customizations panel in the IDE's menu allows managing these settings.

## 1. Operational Guardrails

- **Pre-Commit Verification**: Before marking any task as complete, the agent MUST run `pytest` and ensure all tests pass.
- **Linting Compliance**: All code must pass `flake8` checks. If new code introduces linting errors, the agent must fix them immediately.
- **No Shadow Logic**: Do not implement business logic that isn't requested in requirements. If a logic choice is ambiguous, use `notify_user` to clarify.
- **Ansible-First**: Do not run manual `apt install`, `pip install`, or configuration edits unless experimenting. Once confirmed, IMMEDIATELY port the change to an Ansible role.

## 2. Research & Discovery

- **Codebase Awareness**: Before creating a new utility function or module, the agent MUST search `src/` to check for existing implementations.
- **Dependency Check**: Before adding new libraries to `requirements.txt`, the agent must verify if the functionality is already provided by existing dependencies (numpy, pandas, etc.).

## 3. Communication Standards

- **Task Transparency**: Use `TaskSummary` to explain the *why* behind technical decisions, not just the *what*.
- **Plan Approval**: For any change affecting more than 2 files or introducing new architecture, an `implementation_plan.md` must be created and approved via `notify_user`.

## 4. Coding Style (AI-Specific)

- **Type Hinting**: Mandatory for all new functions. Proactively add hints to existing code when modified.
- **Docstring Standard**: Use Google Style docstrings. Include "Args", "Returns", and "Raises" sections where applicable.
- **Refactoring**: When editing a file, small improvements to readability or standards (like removing unused imports) in that file are encouraged.

## 5. Tool Usage

- **Terminal Execution**: Use the terminal to verify file existence and state before making assumptions.
- **Browser Research**: Use the browser tool to look up documentation for specific library versions used in the project.

## 6. Testing & Quality Assurance

- **Mandatory Unit Tests**: All new Python scripts OR significant functional changes to existing ones MUST include unit tests (using `pytest`) in the `tests/` directory.
- **System Verification**: New Ulauncher extensions or major system configurations (desktop entries, services) MUST be added to the `ansible/verify.yml` playbook.
- **Test Runner**: Always run `./scripts/run_tests.sh` before finalizing work to ensure no regressions in linting, unit tests, or system state.
- **Ansible Lint**: While some pre-existing debt exists, all *new* Ansible code should aim for zero legacy warnings. Use specific tasks instead of generic `shell` where possible.
- **Validate Frontend Assets**: Before verification or deployment, MUST lint/validate all JavaScript and CSS files (e.g., using `eslint` or manual syntax checks) to prevent syntax errors that could break the UI.

## 7. Development Workflow

- **Conventional Commits**: Use `feat:`, `fix:`, `docs:`, or `chore:` prefixes.
- **Python Environment (PEP 668)**: On Ubuntu 24.04, always use `--user --break-system-packages` for persistent system-level Python tool/dependency installation, OR use the project's `./venv/`.
- **Node.js**: Use `community.general.npm` with `global: true` for system-wide CLI tools. Ensure `nodejs` and `npm` are installed via `apt` in the `common` role first.
- **Verification**: After applying an Ansible role, run `ansible-playbook ansible/verify.yml` to ensure the system state matches the intended configuration.
- **Security**: Never commit `~/.ssh/` keys or personal tokens. If a script needs to check for them, it should do so without exposing contents.
- **Git Tracking & Branching**:
  - **NO DIRECT WORK ON MAIN/MASTER**. This branch is for production releases only.
  - **Strict Local Branch Policy**: `feat`, `fix`, `docs`, and `chore` branches are **LOCAL ONLY**. Never push them to origin. Only `develop` and `main` branches are allowed on the remote.
  - Always merge `develop` into your feature branch before requesting a merge back.

### 7.1 Workflows by Commit Type

Adhere to the specific strict workflow for each commit type:

#### 7.1.1 Feature (`feat`)

1. **Docs**: Create `docs/features/name.md` from template.
2. **Branch**: `git checkout -b feat/feature-name`
3. **Work**: Implement changes.
4. **Verify**: Run `scripts/run_tests.sh`.
5. **Merge**: `git merge feat/feature-name` into `develop`.
6. **Push**: **CRITICAL**: Ask for permission -> `git push origin develop`.

#### 7.1.2 Bug Fix (`fix`)

1. **Reproduce**: Create failing test/script.
2. **Branch**: `git checkout -b fix/issue-description`
3. **Fix**: Implement fix.
4. **Verify**: Pass reproduction script AND `scripts/run_tests.sh`.
5. **Merge**: `git merge fix/issue-description` into `develop`.
6. **Push**: **CRITICAL**: Ask for permission -> `git push origin develop`.

#### 7.1.3 Documentation (`docs`)

1. **Branch**: `git checkout -b docs/description`
2. **Work**: Update `README.md`, `docs/`, or artifacts.
3. **Verify**: Check rendering and links.
4. **Merge**: `git merge docs/description` into `develop`.
5. **Push**: **CRITICAL**: Ask for permission -> `git push origin develop`.

#### 7.1.4 Maintenance (`chore`)

1. **Branch**: `git checkout -b chore/description`
2. **Work**: Update configs, dependencies, or gitignore.
3. **Verify**: Run `scripts/run_tests.sh`.
4. **Merge**: `git merge chore/description` into `develop`.
5. **Push**: **CRITICAL**: Ask for permission -> `git push origin develop`.
