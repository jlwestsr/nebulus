---
trigger: always_on
---

# AI Agent Behavior & Operational Rules

This document outlines the specific operational standards and behavioral expectations for AI agents working on this project.

## 0. Agent Configuration & Rule Hierarchy

When opening a project, the Google Antigravity IDE looks first for rules in the local workspace folder before falling back to global system-wide rules.

### Rule Locations
- **Workspace Rules**: The IDE first checks the project's local directory at `your-workspace/agent/rules/`. It may also load configuration from files like `.cursorrules` or `.antigravity/rules.md` within the workspace root.
- **Global Rules**: If no workspace-specific rules are found, the IDE uses the global rule file at `~/.gemini/GEMINI.md`.

### Directory Structure & Use Cases
| Type | Default File Path | Use Case |
|------|-------------------|----------|
| **Workspace Rule** | `your-workspace/agent/rules/` | Project-specific coding standards or restrictions. |
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
    - **Chores**: Minor maintenance or documentation ("chore" work) may be done directly on the `develop` branch.
    - **Features/Bugs**: ALL other work (features, bug fixes, refactors) MUST be done on a new branch (e.g., `feat/...`, `fix/...`) created from `develop`.
    - Always merge `develop` into your feature branch before requesting a merge back.

## 8. Feature Implementation Workflow
When given a directive to work through a feature, follow these steps strictly:
0.  **Create Feature Document**: Create a new file in `docs/features/` using the content from `docs/feature_template.md`. This MUST be the first step to define the feature scope.
1.  **Create a Branch**: Create a new git branch to do the work (e.g., `git checkout -b feat/feature-name`).
2.  **Do the Work**: Implement the changes, following all coding standards and guardrails.
3.  **Test the Work**: Run standard tests (`pytest`, `flake8`) and add new tests as required. Ensure all pass.
4.  **Document the Work**: Update relevant documentation (README, feature docs, walkthrough).
5.  **Commit, Merge, and Push**:
    - Commit changes with conventional messages.
    - Switch to the main development branch (e.g., `develop`).
    - Merge the feature branch.
    - Push the updated branch to the remote.

## 9. Frontend Best Practices
- **Technologies**: Use Vanilla JS, HTML, and CSS (or SCSS) unless a framework is explicitly requested.
- **Namespacing**: Avoid polluting the global window object. Wrap unrelated logic in a global application object (e.g., `MyApp = { ... }`).
- **AJAX**: Use `fetch` (with `async/await`) for all network requests. Ensure robust error handling (try/catch blocks).
- **CSS**: Use specific classes over IDs for styling. Avoid inline styles.
- **HTML Templates**: Large HTML strings should be extracted into constants or template functions to keep logic clean.
