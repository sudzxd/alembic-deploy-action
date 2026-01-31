# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-02-01

### Added
- Python implementation replacing shell script (`src/main.py`)
- Generic State Machine architecture for control flow (`src/machine.py`, `src/states.py`)
- `DangerLevel` StrEnum for type-safe danger levels
- `EnvHandler` class for typed environment variable access
- Centralized constants module (`src/constants.py`)
- Centralized logging module (`src/logger.py`)
- pytest fixtures and unit tests

### Changed
- Refactored CI/CD into separate workflows:
  - `ci.yml` - Linting and unit tests
  - `integration.yml` - End-to-end testing
  - `release.yml` - Manual release automation
  - `validate-published.yml` - Post-release validation
- Updated Dockerfile to use Python entrypoint
- Migrated tests from unittest to pytest

### Removed
- `entrypoint.sh` shell script
- Legacy `test.yml` workflow

## [1.0.0] - 2025-01-15

### Added
- Initial release
- Dry-run mode for SQL preview
- Safety analysis for dangerous operations (DROP, ALTER, TRUNCATE)
- Support for PostgreSQL, MySQL, SQLite
- GitHub Actions outputs for migration status
- Approval workflow integration

[Unreleased]: https://github.com/sudzxd/alembic-deploy-action/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/sudzxd/alembic-deploy-action/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/sudzxd/alembic-deploy-action/releases/tag/v1.0.0
