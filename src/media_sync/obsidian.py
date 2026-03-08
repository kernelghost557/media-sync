"""Obsidian note generator for media items."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Template, Environment, FileSystemLoader

from .models.media import Movie, Series

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = """---
aliases: [{{ title }}]
rating: {{ rating|default(0) }}
watched: {{ watched_date|default("") }}
genres: {{ genres|join(', ') }}
jellyfin_id: {{ jellyfin_id }}
{% if series_id %}series_id: {{ series_id }}{% endif %}
---

# {{ title }} ({{ year|default('N/A') }})

## 📺 Quick Links
- [Play in Jellyfin](http://localhost:8096/web/index.html#!/item?id={{ jellyfin_id }})
{% if series_id %}
- [View in Sonarr](http://localhost:8989/series/{{ series_id }})
{% endif %}

## 🎬 My Review
_Add your thoughts here..._
"""


class ObsidianGenerator:
    """Generate Obsidian markdown notes from media items."""

    def __init__(self, vault_path: Path, template_path: Optional[Path] = None):
        self.vault_path = vault_path.expanduser().resolve()
        self.template_path = template_path.expanduser().resolve() if template_path else None
        self.env = Environment(loader=FileSystemLoader(self.vault_path / "templates" if self.template_path else self.vault_path))
        self._template_cache: Optional[Template] = None

    def _load_template(self) -> Template:
        """Load Jinja2 template."""
        if self._template_cache:
            return self._template_cache
        if self.template_path and self.template_path.exists():
            template_str = self.template_path.read_text()
        else:
            # Use built-in default template
            template_str = DEFAULT_TEMPLATE
        self._template_cache = Environment().from_string(template_str)
        return self._template_cache

    def _sanitize_filename(self, title: str) -> str:
        """Make title filesystem-safe."""
        invalid = '<>:"/\\|?*'
        for ch in invalid:
            title = title.replace(ch, "_")
        # Limit length
        if len(title) > 100:
            title = title[:100]
        return title.strip() + ".md"

    def _determine_folder(self, item: Movie | Series) -> Path:
        """Determine which subfolder in vault to place note."""
        # Simple: all notes in Movies/ or Series/ folders
        if isinstance(item, Series):
            base = self.vault_path / "Series"
        else:
            base = self.vault_path / "Movies"
        # Ensure folder exists
        return base

    def generate_note(self, item: Movie | Series, overwrite: bool = False) -> Optional[Path]:
        """Generate a markdown file for a media item."""
        try:
            folder = self._determine_folder(item)
            folder.mkdir(parents=True, exist_ok=True)
            filename = self._sanitize_filename(item.name)
            file_path = folder / filename

            if file_path.exists() and not overwrite:
                logger.info(f"Note already exists: {file_path}")
                return None

            # Prepare context
            context = {
                "title": item.name,
                "year": item.formatted_year,
                "genres": item.genre,
                "rating": item.community_rating,
                "watched_date": None,  # TODO: get from Jellyfin playback info
                "jellyfin_id": item.id,
                "series_id": item.id if isinstance(item, Series) else None,
            }

            template = self._load_template()
            content = template.render(**context)

            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Created note: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to generate note for {item.name}: {e}")
            return None