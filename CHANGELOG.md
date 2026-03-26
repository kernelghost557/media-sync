# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI pipeline (lint, type-check, test, coverage)
- Pre-commit hooks (ruff, mypy, pytest)
- Type checking with mypy (strict mode)
- Coverage reporting via Codecov
- Badges in README for CI and coverage
- Initial implementation of SyncEngine
- Basic Obsidian note generation from Jellyfin movies and series
- Healthcheck command implementation
- Additional tests for SyncEngine
- Radarr client and sync_radarr method (v0.3.0)
- Templates now include Radarr links for movies
- Support for Radarr ratings and genres in movie notes
- CLI: added `--source` option to sync specific service

### Changed
- Updated README with development instructions, project structure, and badges
- CLI healthcheck now performs actual connectivity tests
- SyncEngine uses separate templates for movies and series
- Radarr integration marked as stable in documentation

### Fixed
- Fixed potential directory creation in dry-run mode (now logs only)

## [0.4.0] - 2026-03-xx

### Added
- Reddit Warmup integration: daily collection of fresh posts from r/selfhosted, r/python, r/homelab with trend analysis stored in MEMORY.md
- Favorites filtering: sync only marked favorites from Jellyfin (config option `sync_favorites_only`)
- Improved console output with Rich library

### Changed
- Clarified feature set; Radarr is now fully supported (not experimental)

### Fixed
- Minor bugfixes in config loading and template rendering
