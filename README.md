# 🎬 media-sync

> **Synchronize your media universe.** Connect Jellyfin, Sonarr, Radarr, and Obsidian into one seamless workflow.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/KernelGhost/media-sync/actions/workflows/ci.yml/badge.svg)](https://github.com/KernelGhost/media-sync/actions)
[![codecov](https://codecov.io/gh/KernelGhost/media-sync/branch/main/graph/badge.svg)](https://codecov.io/gh/KernelGhost/media-sync)
[![PyPI version](https://badge.fury.io/py/media-sync.svg)](https://badge.fury.io/py/media-sync)

---

## 🤖 What is this?

`media-sync` is a **command-line powerhouse** that automatically synchronizes metadata between your media servers and your knowledge base. No more manual copying. No more lost ratings. Everything talks to everything.

### Perfect for:
- **Home lab enthusiasts** running Jellyfin + Sonarr/Radarr stacks
- **Obsidian users** who want automatic notes for every movie/series they watch
- **Power users** who hate duplicate work across apps
- ** anyone** who wants their media ecosystem to *just work*

---

## ⚡ Features

| ✅ | Feature | Why it matters |
|----|---------|----------------|
| 🎯 | **Bi-directional sync** | Rate a movie in Jellyfin → appears in Obsidian. Edit a note in Obsidian → updates Jellyfin (experimental). |
| 🔄 | **Real-time watching status** | "Watched" in Jellyfin = automatically marked in Obsidian with timestamp. |
| 🏷️ | **Tag propagation** | Tags from Sonarr/Radarr flow to Obsidian frontmatter. Filter and query like a boss. |
| 📊 | **Rich console output** | Beautiful progress bars, colored logs, and clear error messages (powered by `rich`). |
| 🧩 | **Multiple profiles** | Separate configs for "home", "office", "vpn" — switch with one flag. |
| ⚙️ | **Flexible config** | YAML file, environment variables, or `.env` — your choice. |
| 🧪 | **Tested & reliable** | 80%+ coverage, CI pipeline, pre-commit hooks. |
| 🚀 | **Fast & lightweight** | Pure Python, async-ready, minimal dependencies. |

---

## 🚀 Installation

### Via pip (recommended)
```bash
pipx install media-sync   # isolated, no clutter
# or
pip install media-sync
```

### Via Poetry (for development)
```bash
poetry add media-sync
```

### From source
```bash
git clone https://github.com/KernelGhost/media-sync.git
cd media-sync
poetry install
poetry run media-sync --help
```

---

## 📖 Quick Start

### 1️⃣ Initialize configuration
```bash
media-sync config init
```
Edits `~/.config/media-sync/config.yaml` (or sets `.env`). Example:

```yaml
jellyfin:
  url: "http://localhost:8096"
  api_key: "YOUR_JELLYFIN_API_KEY"

obsidian:
  vault_path: "/home/user/Documents/obsidian-vault"
  template: "templates/media_note.md"   # optional

sonarr:
  url: "http://localhost:8989"
  api_key: "YOUR_SONARR_API_KEY"

radarr:
  url: "http://localhost:7878"
  api_key: "YOUR_RADARR_API_KEY"
```

### 2️⃣ Test connection
```bash
media-sync healthcheck
```
Output:
```
[green]✓[/green] Jellyfin: OK (API v10.8)
[green]✓[/green] Obsidian: Vault found, template OK
[yellow]⚠[/yellow] Sonarr: not configured (skipped)
```

### 3️⃣ Run your first sync
```bash
# One-way: Jellyfin → Obsidian
media-sync sync jellyfin-to-obsidian

# Full bidirectional (experimental)
media-sync sync full --dry-run   # preview changes
media-sync sync full             # apply
```

**What you'll see:**
```
╭─ Synchronization started ─╮
│ Mode: jellyfin-to-obsidian │
├────────────────────────────┤
│ ✓ Connected to Jellyfin    │
│ ✓ Fetched 124 media items  │
│ ✓ Synced 118 notes         │
│ ⚠ 6 skipped (missing)      │
╰────────────────────────────╯
```

---

## 🎯 Use Cases

### 📺 You just watched a movie in Jellyfin
→ `media-sync` creates an Obsidian note with:
- Title, year, rating, genres
- Your watch timestamp
- Direct link to play via Jellyfin
- Ready for your thoughts/review

### 📺 Your Plex/Jellyfin library is huge, but your Obsidian vault is empty
→ Run `media-sync sync jellyfin-to-obsidian` once. All metadata imported. Organize with Dataview queries.

### 📺 You adjust ratings in Sonarr
→ Changes propagate to Obsidian frontmatter → your dashboards update automatically.

---

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `media-sync config init` | Create default config file |
| `media-sync healthcheck` | Test all connections |
| `media-sync sync <mode>` | Run synchronization (`jellyfin-to-obsidian`, `obsidian-to-jellyfin`, `full`) |
| `media-sync version` | Show version |
| `media-sync --help` | Full help |

---

## 📁 Obsidian Template Example

`templates/media_note.md`:
```markdown
---
aliases: [{{ title }}]
rating: {{ rating }}
watched: {{ watched_date }}
genres: {{ genres | join(', ') }}

jellyfin_id: {{ jellyfin_id }}
sonarr_id: {{ sonarr_id }}
radarr_id: {{ radarr_id }}
---

# {{ title }} ({{ year }})

## 📺 Quick Links
- [Play in Jellyfin](http://localhost:8096/web/index.html#!/item?id={{ jellyfin_id }})
- [View in Sonarr](http://localhost:8989/series/{{ sonarr_id }})
- [View in Radarr](http://localhost:7878/movie/{{ radarr_id }})

## 🎬 My Review
_Add your thoughts here..._
```

---

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/KernelGhost/media-sync.git
cd media-sync
poetry install

# Run tests
poetry run pytest --cov

# Lint
poetry run ruff check src tests

# Pre-commit hooks
pre-commit install
```

---

## 📜 License

MIT © 2025–present [KernelGhost](https://github.com/KernelGhost)

---

## 🙋 Support

- **Issues:** https://github.com/KernelGhost/media-sync/issues
- **Discussions:** https://github.com/KernelGhost/media-sync/discussions
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

*Built with ❤️ for the self-hosted media community. If this tool saves you time, consider starring the repo ⭐*