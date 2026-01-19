# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Frontend**: Fully migrated from Open WebUI to **Nebulus Gantry** (Chainlit-based).
- **Core**: Removed Open WebUI service and artifacts.
- **UI**: Implemented friendly model names in Gantry.
- **Chat**: Added `/clear_all` command for bulk deletion of chat history.

## [0.1.0] - 2025-12-30

### Added
- Initial release of Nebulus (formerly Black Box AI System).
- Core CLI tool `nebulus` for managing services.
- Containerized AI stack (Ollama, Open WebUI, ChromaDB).
- Custom MCP Server for tool integration.
- Backup and restore functionality.
- Automated system setup via Ansible.
