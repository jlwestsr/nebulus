# Project Context & Coding Standards

## Project Overview
This is a production-grade AI engineering project. 

## Coding Standards
1. **Unit Tests**: ALL changes must have accompanying unit tests in the `tests/` directory.
2. **Modular Code**: Do not put business logic in notebooks. Move logic to `src/` modules.
3. **Type Hinting**: Use Python type hints for all function definitions.
4. **Documentation**: All public functions must have docstrings (Google style).

## Git Workflow
1. We use Git Flow.
2. Direct commits to `main` are forbidden. 
3. Work on feature branches off `develop`.
4. Ensure `git init` and `.gitignore` are respected.

## File Structure
- `data/` and `models/` are ignored by git.
- `src/` contains the source code.
- `tests/` mirrors the structure of `src/`.