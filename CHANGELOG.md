# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-01-10

### Added

- **Core Synchronization**: Automated sync of disliked albums from Plex to Lidarr
- **Plex Integration**: Read from Plex Smart Playlists to identify disliked albums
- **Lidarr Integration**: Automatic tag creation and application to albums
- **Tag Management**: `get_or_create_tag()` function for managing Lidarr tags
- **Environment Configuration**: Support for 10 configurable environment variables via `.env`
- **Dry-Run Mode**: Safe-by-default preview mode (enabled by default)
- **Timeout Configuration**: Configurable `REQUEST_TIMEOUT` environment variable (default: 10 seconds)
- **Comprehensive Logging**: Structured logging with timestamps and log levels
- **Environment Validation**: Automatic validation of required environment variables at startup
- **Error Handling**: Robust exception handling for network errors, timeouts, and API failures
- **Type Hints**: Full Python type annotations for all functions
- **Documentation**: Google-style docstrings for all functions and module
- **Docker Support**: Fully containerized application with Docker and Docker Compose
- **Docker Image**: Lightweight `python:3.12-slim` base image
- **Cron Integration**: Designed for easy scheduling via system cron jobs
- **Configuration Template**: `.env-example` file for quick setup
- **Comprehensive README**: Detailed setup, usage, and workflow documentation

### Features

#### Safety & Control

- Dry-run mode prevents accidental modifications
- Request timeout protection against hanging connections
- Validation of all required configuration at startup
- Detailed logging of all operations
- Graceful error handling with informative messages

#### Deployment

- Docker containerization for consistent environments
- Docker Compose for simplified orchestration
- Cron scheduling support for nightly automation
- Lightweight container image (Python 3.12-slim base)
- No external dependencies beyond Python packages

#### Configuration

- Environment variable-based configuration
- Support for custom Lidarr tag names
- Configurable API request timeouts
- Configurable rating thresholds
- Optional dry-run mode for testing

### Technical Details

- **Language**: Python 3.12
- **Dependencies**:
  - `plexapi` - Plex API client library
  - `requests` - HTTP client with timeout support
  - `python-dotenv` - Environment file support
- **Code Quality**:
  - Full type hints throughout codebase
  - Google-style docstrings for all functions
  - Structured logging instead of print statements
  - Exception handling for network and API errors
  - Passes `ruff` linting checks

### Known Limitations

- Requires Plex Pass for Smart Playlist support
- One-directional sync (Plex → Lidarr only)
- Designed for Linux environments (Docker-based)
- No support for removing previously applied tags

### Documentation

- [README.md](README.md) - Installation and usage guide
- [RELEASE_NOTES.md](RELEASE_NOTES.md) - Initial release details
- Module docstrings - Comprehensive function documentation
- `.env-example` - Configuration template with descriptions

---

[Unreleased]: https://github.com/tobus3000/plex-lidarr-sync/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/tobus3000/plex-lidarr-sync/releases/tag/v1.0.0
