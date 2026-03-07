# media-sync

CLI tool to synchronize metadata between Jellyfin, Sonarr, Radarr and Obsidian.

## Features

- Sync watched status, ratings, tags from Jellyfin to Obsidian
- Sync series/movie metadata from Sonarr/Radarr to Obsidian
- Bi-directional sync: changes in Obsidian can update Jellyfin (experimental)
- Rich console output with progress bars
- Configuration via YAML or environment variables
- Supports multiple profiles

## Installation

```bash
pipx install media-sync
# or
pip install media-sync
```

## Quick Start

```bash
# Configure credentials
media-sync config init

# Test connectivity
media-sync healthcheck

# Run one-way sync (Jellyfin -> Obsidian)
media-sync sync jellyfin-to-obsidian

# Full bidirectional sync (experimental)
media-sync sync full
```

## Configuration

Create a `.env` file or run `media-sync config init`:

```yaml
jellyfin:
  url: "http://localhost:8096"
  api_key: "YOUR_API_KEY"

obsidian:
  vault_path: "/path/to/vault"
  template: "templates/media_note.md"
```

## Development

```bash
poetry install
poetry run pytest
pre-commit install
```

## License

MIT © KernelGhost