# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-08

### Added
- **Sonarr integration**: SonarrClient API wrapper (series retrieval, healthcheck)
- **Radarr integration**: RadarrClient API wrapper (movies retrieval, healthcheck)
- **Enhanced sync engine**: `sync_sonarr()`, `sync_radarr()`, `sync_all()` with per-source stats
- **CLI improvements**: `--source` option (`jellyfin|sonarr|radarr|all`), default `all`
- **Configuration**: Sonarr/Radarr config models, environment variable support (`SONARR_URL`, `RADARR_API_KEY`, etc.)
- **Model mapping**: Convert Sonarr series and Radarr movies to internal `Series`/`Movie` models
- **Documentation**: Updated README with Sonarr/Radarr examples, usage, and roadmap
- **Unit tests**: `test_sonarr_radarr.py` (client mocks), `test_config_sonarr_radarr.py`

### Changed
- `sync` command now supports multiple sources
- README restructured with clearer Quick Start and feature table

---

## [0.1.0] - 2026-03-07

### Added
- Initial project structure with Poetry, ruff, pytest, pre-commit
- CLI with commands: `healthcheck`, `sync`, `config-init`
- Basic scaffolding for configuration management
- GitHub Actions CI pipeline (pytest + coverage + ruff)
- Unit tests for CLI using click.testing
- .gitignore, README with installation and usage
- First release on GitHub

[0.1.0]: https://github.com/KernelGhost/media-sync/releases/tag/v0.1.0