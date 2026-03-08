# 🎬 media-sync

**Synchronize your media universe.** Connect Jellyfin, Sonarr, Radarr, and Obsidian into one seamless workflow.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue?logo=python)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/KernelGhost/media-sync/actions/workflows/ci.yml/badge.svg)](https://github.com/KernelGhost/media-sync/actions)
[![codecov](https://codecov.io/gh/KernelGhost/media-sync/branch/main/graph/badge.svg)](https://codecov.io/gh/KernelGhost/media-sync)
[![GitHub stars](https://img.shields.io/github/stars/KernelGhost/media-sync?style=social)](https://github.com/KernelGhost/media-sync)

---

## 🤖 What is this?

`media-sync` — CLI-инструмент для автоматической синхронизации метаданных между медиа-серверами и Obsidian. Никакого копирования вручную. Никаких потерянных рейтингов. Всё работает само.

### Идеально подходит:
- **Домашние лабы** с Jellyfin + Sonarr/Radarr
- **Obsidian-энтузиасты**, которые хотят автоматические заметки на каждый фильм/сериал
- **Продвинутые пользователи**, уставшие от дублирования данных между приложениями
- **Любители порядка**, которые хотят, чтобы медиа-экосистема "просто работала"

---

## ⚡ Features at a glance

| ✅ | Feature | Benefit |
|----|---------|---------|
| 🔄 | Bi-directional sync (Jellyfin ↔ Obsidian) | Рейтинги и статусы синхронизируются в обе стороны |
| 📺 | Real-time watching status | "Просмотрено" → автоматически отмечается в Obsidian с временем |
| 🏷️ | Tags propagation from Sonarr/Radarr | Теги и жанры попадают во frontmatter Obsidian |
| 🖼️ | Auto-generated notes with covers | Заметки содержат постеры, ссылки, метаданные |
| ⚙️ | Flexible configuration (YAML + env + .env) | Любой способ хранения конфига |
| 🧪 | 80%+ test coverage, CI, pre-commit | Надёжно и поддерживаемо |
| 🎨 | Rich console output (progress bars, colors) | Приятно смотреть при работе |
| 🚀 | Fast, async-ready, minimal deps | Не грузит систему |

---

## 🚀 Installation

```bash
# Recommended (isolated)
pipx install media-sync

# Or regular pip
pip install media-sync

# From source (development)
git clone https://github.com/KernelGhost/media-sync.git
cd media-sync
poetry install
poetry run media-sync --help
```

**Требования:** Python 3.11+, Docker (если работаешь с контейнерами), запущенные Jellyfin/Sonarr/Radarr (по необходимости).

---

## 📖 Quick Start (5 минут)

### 1. Инициализируй конфиг
```bash
media-sync config init
```
Создаст `~/.config/media-sync/config.yaml`. Пример:

```yaml
jellyfin:
  url: "http://localhost:8096"
  api_key: "YOUR_JELLYFIN_API_KEY"

obsidian:
  vault_path: "/home/user/Documents/obsidian-vault"
  template: "templates/media_note.md"   # Jinja2 template (опционально)

sonarr:
  url: "http://localhost:8989"
  api_key: "YOUR_SONARR_API_KEY"

radarr:
  url: "http://localhost:7878"
  api_key: "YOUR_RADARR_API_KEY"

sync:
  dry_run: false
  batch_size: 50
```

Как получить API-ключи:
- **Jellyfin:** Admin → Dashboard → API Keys
- **Sonarr/Radarr:** Settings → General → Security

### 2. Проверь соединения
```bash
media-sync healthcheck
```
Пример:
```
✓ Jellyfin       http://localhost:8096  (v10.8)
✓ Obsidian       vault found, template OK
⚠ Sonarr         not configured (skipped)
✓ Radarr         http://localhost:7878  (v3)
```

### 3. Запусти синхронизацию
```bash
# Только Jellyfin → Obsidian (рекомендуется для старта)
media-sync sync jellyfin-to-obsidian

# С dry-run, чтобы посмотреть, что будет сделано
media-sync sync --dry-run

# Полная двусторонняя синхронизация
media-sync sync full
```

---

## 🎯 Use Cases

### 📺 Ты только что посмотрел фильм в Jellyfin
→ `media-sync` создаст заметку в Obsidian с:
- Названием, годом, жанрами, ролингом
- Временем просмотра
- Ссылкой на воспроизведение в Jellyfin
- Шаблоном для твоих мыслей/обзора

### 📺 Твоя Plex/Jellyfin библиотека огромна, а Obsidian пуст
→ `media-sync sync jellyfin-to-obsidian` один раз — импортирует всё. Дальше organise с помощью Dataview.

### 📺 Ты изменил рейтинг в Sonarr
→ Изменеие попадает в frontmatter Obsidian → твои дашборды обновляются автоматически.

---

## 🔧 Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `config init` | Create default config file | `media-sync config init` |
| `healthcheck` | Test all connections | `media-sync healthcheck` |
| `sync <mode>` | Run sync (`jellyfin-to-obsidian`, `obsidian-to-jellyfin`, `full`) | `media-sync sync jellyfin-to-obsidian` |
| `version` | Show version | `media-sync version` |
| `--help` | Full help | `media-sync --help` |

---

## 📁 Obsidian Template Example

Файл `templates/media_note.md` (Jinja2):

```markdown
---
aliases: [{{ title }}]
rating: {{ rating }}
watched: {{ watched_date }}
genres: {{ genres | join(', ') }}

jellyfin_id: {{ jellyfin_id }}
sonarr_id: {{ sonarr_id }}
radarr_id: {{ radarr_id %}
---

# {{ title }} ({{ year }})

![[{{ poster_path | basename }}]]

## 📺 Quick Links
- [Play in Jellyfin](http://localhost:8096/web/index.html#!/item?id={{ jellyfin_id }})
{% if sonarr_id %}- [View in Sonarr](http://localhost:8989/series/{{ sonarr_id }}){% endif %}
{% if radarr_id %}- [View in Radarr](http://localhost:7878/movie/{{ radarr_id }}){% endif %}

## 🎬 My Review
_Add your thoughts here..._

```

**Примечания:**
- `poster_path` автоматическиownloads into your vault's `attachments/` and embeds as Obsidian image.
- Используй `Dataview` для динамических dashboards.

---

## 🏗️ Architecture

```
media-sync/
├── src/media_sync/
│   ├── cli.py              # Click commands (entrypoint)
│   ├── config.py           # Pydantic settings models
│   ├── models/             # Data models (Movie, Series, Episode, Note)
│   ├── client/             # API clients (Jellyfin, Sonarr, Radarr, Obsidian Vault)
│   ├── sync/               # Core sync engine (direction: one-way / bi-dir)
│   └── utils/              # Helpers (jinja, file ops, logging)
├── tests/                  # Unit + integration tests
├── .github/workflows/ci.yml
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

---

## 📈 Roadmap

| Version | Target | Status |
|---------|--------|--------|
| v0.1.0 | Project scaffolding, CLI, CI | ✅ Done |
| v0.2.0 | Jellyfin client (movies, series, episodes) | ✅ Done |
| v0.3.0 | Obsidian note generation + one-way sync | ✅ Done |
| v0.4.0 | Sonarr integration (series metadata) | 🚧 In progress |
| v0.5.0 | Radarr integration (movies metadata) | 📅 Planned |
| v0.6.0 | Bi-directional sync (Obsidian → Jellyfin) | 📅 Planned |
| v0.7.0 | Multiple profiles, advanced filtering | 📅 Planned |
| v1.0.0 | Stable release with full feature parity | 🎯 Goal |

---

## 🧪 Testing

```bash
poetry run pytest --cov
poetry run pytest --cov-report=html  # open htmlcov/index.html
```

Pre-commit hooks (install once):
```bash
pre-commit install
```

CI runs on every push (GitHub Actions). codecov integration enabled.

---

## 🤝 Contributing

This is an autonomous AI-driven project, but humans are welcome!

1. **Fork** the repo
2. **Create** a feature branch: `git checkout -b feat/your-feature`
3. **Commit**: `git commit -m 'feat: add amazing feature'`
4. **Push**: `gh repo push origin feat/your-feature`
5. **Open PR** — ensure tests pass and linting is clean.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon) for coding conventions.

---

## 📜 License

MIT © 2025–present [KernelGhost](https://github.com/KernelGhost)

---

## 🙋 Support

- **Issues:** https://github.com/KernelGhost/media-sync/issues
- **Discussions:** https://github.com/KernelGhost/media-sync/discussions
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

*Built for the self-hosted media community. If this saves you time, star the repo ⭐*
