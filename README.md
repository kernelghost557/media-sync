# 🎬 media-sync

> **Synchronize your media universe.** Connect Jellyfin, Sonarr, Radarr, and Obsidian into one seamless workflow.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/KernelGhost/media-sync/actions/workflows/ci.yml/badge.svg)](https://github.com/KernelGhost/media-sync/actions)
[![codecov](https://codecov.io/gh/KernelGhost/media-sync/branch/main/graph/badge.svg)](https://codecov.io/gh/KernelGhost/media-sync)

---

## 🤖 What is this?

`media-sync` is a command-line tool that automatically synchronizes metadata from media servers to Obsidian. No more manual copying. Everything talks to everything.

### Perfect for:
- Home lab enthusiasts running Jellyfin + Sonarr/Radarr stacks
- Obsidian users who want automatic notes for every movie/series they watch
- Power users who hate duplicate work across apps

---

## ⚡ Features (v0.2.0)

| ✅ | Feature |
|----|---------|
| 🎯 | **One-way sync: Jellyfin → Obsidian** (movies + series) |
| 🏷️ | **Frontmatter generation** with aliases, rating, genres, jellyfin_id |
| 🔗 | **Quick links** to play in Jellyfin directly from Obsidian |
| 🩺 | **Healthcheck** to verify all service connections |
| 📊 | **Rich console output** with progress bars and colored logs |
| ⚙️ | **Flexible config** via YAML, environment variables, or `.env` |
| 🧪 | **Tested & reliable** with CI, coverage, and pre-commit hooks |
| 🚀 | **Fast & lightweight** pure Python, minimal dependencies |

*Note: Sonarr/Radarr integration and bi-directional sync are planned for future releases.*

---

## 🚀 Installation

```bash
pipx install media-sync   # recommended, isolated
# or
pip install media-sync

# From source (development)
git clone https://github.com/KernelGhost/media-sync.git
cd media-sync
poetry install
```

---

## 📖 Quick Start

### 1️⃣ Create config

```bash
media-sync config init
```

This creates `~/.config/media-sync/config.yaml`. Example:

```yaml
jellyfin:
  url: "http://localhost:8096"
  api_key: "YOUR_JELLYFIN_API_KEY"

obsidian:
  vault_path: "/path/to/your/vault"
  template: "templates/media_note.md"   # optional, built-in default exists

# Optional (not yet used in sync):
# sonarr:
#   url: "http://localhost:8989"
#   api_key: "YOUR_SONARR_API_KEY"
#
# radarr:
#   url: "http://localhost:7878"
#   api_key: "YOUR_RADARR_API_KEY"
```

### 2️⃣ Verify connections

```bash
media-sync healthcheck
```

Example output:
```
✓ Jellyfin: OK (API v10.8)
✓ Obsidian: Vault found
⚠ Sonarr: not configured (skipped)
✓ Radarr: not configured (skipped)
```

### 3️⃣ Sync your library

```bash
# Preview what would be synced (no files written)
media-sync sync --source jellyfin --dry-run

# Actually sync movies and series from Jellyfin to Obsidian
media-sync sync --source jellyfin
```

Notes are created in `Obsidian vault/Movies/` and `Obsidian vault/Series/` with metadata and links.

---

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `media-sync config init` | Create default config file |
| `media-sync healthcheck` | Test connectivity to configured services |
| `media-sync sync --source jellyfin` | Sync movies and series from Jellyfin to Obsidian |
| `media-sync sync --source all` | Sync all configured sources (Sonarr/Radarr pending) |
| `media-sync --help` | Full help |

---

## 📁 Template

By default, `media-sync` uses an internal Jinja2 template. You can override it by setting `template:` in config and creating the file.

Example (`templates/media_note.md`):

```markdown
---
aliases: [{{ title }}]
rating: {{ rating }}
watched: {{ watched_date }}
genres: {{ genres | join(', ') }}
jellyfin_id: {{ jellyfin_id }}
---

# {{ title }} ({{ year }})

## 📺 Quick Links
- [Play in Jellyfin]({{ jellyfin_url }}/web/index.html#!/item?id={{ jellyfin_id }})

## 🎬 My Review
_Add your thoughts here..._
```

The template receives context: `title`, `year`, `rating`, `watched_date`, `genres`, `jellyfin_id`, `jellyfin_url`.

---

## 🏗️ Project Structure

```
media-sync/
├── src/media_sync/
│   ├── cli.py              # Click commands
│   ├── config.py           # Pydantic config models
│   ├── config_loader.py    # Load YAML + env overrides
│   ├── models/             # Data models (Movie, Series, Episode)
│   ├── client/             # API clients (Jellyfin, Sonarr, Radarr)
│   └── sync.py             # SyncEngine (Jellyfin → Obsidian)
├── tests/                  # Unit tests
├── templates/              # Default template (optional)
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── pyproject.toml
├── CHANGELOG.md
└── README.md
```

---

## 🧪 Development

```bash
# Install dependencies
poetry install

# Run tests with coverage
poetry run pytest --cov

# Lint
poetry run ruff check src tests

# Type checking
poetry run mypy src tests

# Pre-commit (runs lint, type-check, tests on commit)
pre-commit install
```

---

## 📈 Roadmap

- [x] v0.1.0 — Project scaffolding, CLI, CI
- [x] v0.2.0 — Jellyfin client + Obsidian note generation (one-way)
- [ ] v0.3.0 — Sonarr integration (series metadata)
- [ ] v0.4.0 — Radarr integration (movies metadata)
- [ ] v0.5.0 — Bi-directional sync (Obsidian → Jellyfin)
- [ ] v0.6.0 — Multiple profiles, advanced filtering
- [ ] v1.0.0 — Stable release

---

## 🤝 Contributing

This is an autonomous AI-driven project, but human collaboration is welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`gh repo push origin feat/amazing-feature`)
5. Open a Pull Request

Please ensure tests pass and linting is clean before submitting.

---

## 🙋 Support

- **Issues:** https://github.com/KernelGhost/media-sync/issues
- **Discussions:** https://github.com/KernelGhost/media-sync/discussions
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 📜 License

MIT © 2025–present [KernelGhost](https://github.com/KernelGhost)

---

*Built with ❤️ for the self-hosted media community. If this tool saves you time, consider starring the repo ⭐*
