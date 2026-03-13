"""Synchronization engine for media metadata."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Template

from .client.jellyfin import JellyfinClient
from .client.sonarr import SonarrClient
from .client.radarr import RadarrClient
from .models.media import Movie, Series

logger = logging.getLogger(__name__)

# Default templates if none provided
DEFAULT_MOVIE_TEMPLATE = """---
aliases: [{{ title }}]
rating: {{ rating }}
watched: {{ watched_date }}
genres: {{ genres | join(', ') }}
jellyfin_id: {{ jellyfin_id }}
{% if sonarr_id %}sonarr_id: {{ sonarr_id }}{% endif %}
{% if radarr_id %}radarr_id: {{ radarr_id }}{% endif %}
---

# {{ title }} ({{ year }})

## 📺 Quick Links
- [Play in Jellyfin]({{ jellyfin_url }}/web/index.html#!/item?id={{ jellyfin_id }})
{% if sonarr_id %}- [View in Sonarr]({{ sonarr_url }}/series/{{ sonarr_id }}){% endif %}
{% if radarr_id %}- [View in Radarr]({{ radarr_url }}/movie/{{ radarr_id }}){% endif %}

## 🎬 My Review
_Add your thoughts here..._
"""

DEFAULT_SERIES_TEMPLATE = """---
aliases: [{{ title }}]
rating: {{ rating }}
genres: {{ genres | join(', ') }}
status: {{ status }}
season_count: {{ season_count }}
episode_count: {{ episode_count }}
jellyfin_id: {{ jellyfin_id }}
{% if sonarr_id %}sonarr_id: {{ sonarr_id }}{% endif %}
---

# {{ title }} ({{ year }})

**Status:** {{ status }}  
**Seasons:** {{ season_count }}  
**Episodes:** {{ episode_count }}

## 📺 Quick Links
- [Play in Jellyfin]({{ jellyfin_url }}/web/index.html#!/item?id={{ jellyfin_id }})
{% if sonarr_id %}- [View in Sonarr]({{ sonarr_url }}/series/{{ sonarr_id }}){% endif %}

## 📝 Episodes
<!-- optional: list episodes, could be generated dynamically -->

## 🎬 My Review
_Add your thoughts here..._
"""


class SyncEngine:
    """Engine to synchronize media from servers to Obsidian vault."""

    def __init__(self, config):
        self.config = config
        self.jellyfin_client = None
        self.sonarr_client = None
        self.radarr_client = None
        self.vault_path = None
        self.template_str = None

        # Initialize clients based on config
        if config.jellyfin:
            self.jellyfin_client = JellyfinClient(
                base_url=config.jellyfin.url,
                api_key=config.jellyfin.api_key,
                user_id=config.jellyfin.username,
            )
        if config.sonarr:
            self.sonarr_client = SonarrClient(
                base_url=config.sonarr.url,
                api_key=config.sonarr.api_key,
            )
        if config.radarr:
            self.radarr_client = RadarrClient(
                base_url=config.radarr.url,
                api_key=config.radarr.api_key,
            )
        if config.obsidian:
            self.vault_path = config.obsidian.vault_path.expanduser().resolve()
            if config.obsidian.template:
                template_path = config.obsidian.template.expanduser().resolve()
                if template_path.exists():
                    self.template_str = template_path.read_text()
            # Note: if template_str is still None, _get_template will use built-in defaults

        logger.info("SyncEngine initialized")

    def _get_template(self, media_type: str) -> Template:
        """Select appropriate template string based on media type."""
        if self.template_str:
            return Template(self.template_str)
        # Choose default based on type
        if media_type == "series":
            return Template(DEFAULT_SERIES_TEMPLATE)
        return Template(DEFAULT_MOVIE_TEMPLATE)

    def _write_note(self, path: Path, content: str, dry_run: bool) -> bool:
        """Write note to file if not dry-run."""
        if dry_run:
            logger.info(f"[DRY RUN] Would write: {path}")
            return True
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text(content)
                logger.info(f"Created note: {path}")
                return True
            else:
                # Optionally update if changed? For now skip.
                logger.debug(f"Note already exists: {path}")
                return False
        except Exception as e:
            logger.error(f"Failed to write {path}: {e}")
            return False

    def _render_movie_note(self, movie: Movie) -> str:
        """Render a movie note using template."""
        template = self._get_template("movie")
        # Use production_year as year
        year = movie.production_year or ""
        # Only include watched_date if we have rating (assume watched if rated)
        watched_date = datetime.now().strftime("%Y-%m-%d") if movie.community_rating else ""
        context = {
            "title": movie.name,
            "year": year,
            "rating": movie.community_rating or "",
            "watched_date": watched_date,
            "genres": movie.genre or [],
            "jellyfin_id": movie.id,
            "jellyfin_url": self.config.jellyfin.url if self.config.jellyfin else "",
            "sonarr_id": None,
            "sonarr_url": "",
            "radarr_id": None,
            "radarr_url": "",
        }
        return template.render(**context)

    def _render_series_note(self, series: Series) -> str:
        """Render a series note using template."""
        template = self._get_template("series")
        year = series.production_year or ""
        context = {
            "title": series.name,
            "year": year,
            "rating": series.community_rating or "",
            "genres": series.genre or [],
            "status": series.status or "",
            "season_count": series.season_count or 0,
            "episode_count": series.episode_count or 0,
            "jellyfin_id": series.id,
            "jellyfin_url": self.config.jellyfin.url if self.config.jellyfin else "",
            "sonarr_id": None,
            "sonarr_url": "",
        }
        return template.render(**context)

    def sync_jellyfin(self, dry_run: bool = False) -> Dict[str, int]:
        """Sync movies and series from Jellyfin to Obsidian."""
        if not self.jellyfin_client:
            raise ValueError("Jellyfin client not configured")
        if not self.vault_path:
            raise ValueError("Obsidian vault not configured")

        stats = {"movies": 0, "series": 0, "created": 0, "skipped": 0, "errors": 0}
        # Movies
        try:
            movies = self.jellyfin_client.get_movies(include_favorite=False)
            stats["movies"] = len(movies)
            for movie in movies:
                try:
                    content = self._render_movie_note(movie)
                    safe_title = "".join(c for c in movie.name if c.isalnum() or c in " -_").strip()
                    filename = f"{safe_title} ({movie.year or 'Unknown'}).md"
                    path = self.vault_path / "Movies" / filename
                    if self._write_note(path, content, dry_run):
                        stats["created"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing movie {movie.name}: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch movies: {e}")
            stats["errors"] += 1

        # Series
        try:
            series_list = self.jellyfin_client.get_series()
            stats["series"] = len(series_list)
            for series in series_list:
                try:
                    content = self._render_series_note(series)
                    safe_title = "".join(c for c in series.name if c.isalnum() or c in " -_").strip()
                    filename = f"{safe_title} ({series.year or 'Unknown'}).md"
                    path = self.vault_path / "Series" / filename
                    if self._write_note(path, content, dry_run):
                        stats["created"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing series {series.name}: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch series: {e}")
            stats["errors"] += 1

        return stats

    def sync_sonarr(self, dry_run: bool = False) -> Dict[str, int]:
        """Sync series from Sonarr to Obsidian."""
        if not self.sonarr_client:
            raise ValueError("Sonarr client not configured")
        if not self.vault_path:
            raise ValueError("Obsidian vault not configured")

        stats = {"series": 0, "created": 0, "skipped": 0, "errors": 0}
        try:
            series_list = self.sonarr_client.get_series()
            stats["series"] = len(series_list)
            for series in series_list:
                try:
                    # Sonarr series dict fields: id, title, seriesYear, status, seasonCount, genres, ratings
                    series_id = series.get("id")
                    title = series.get("title", "Unknown")
                    year = series.get("seriesYear") or series.get("year") or ""
                    status = series.get("status", "")
                    season_count = series.get("seasonCount", 0)
                    # genres might be list of strings or list of objects
                    genres_raw = series.get("genres", [])
                    genres = [g if isinstance(g, str) else g.get("name", "") for g in genres_raw if g]
                    # rating from community rating or user rating
                    rating = None
                    ratings = series.get("ratings", {})
                    if ratings:
                        # Jellyfin-style: ratings might have "CommunityRating" or "VoteCount"
                        rating = ratings.get("CommunityRating") or ratings.get("value")
                        if rating:
                            rating = float(rating)

                    # Render note
                    template = self._get_template("series")
                    context = {
                        "title": title,
                        "year": year,
                        "rating": rating or "",
                        "genres": genres,
                        "status": status,
                        "season_count": season_count,
                        "episode_count": 0,  # we could sum episodes but O(n) extra call
                        "jellyfin_id": None,
                        "jellyfin_url": "",
                        "sonarr_id": series_id,
                        "sonarr_url": self.config.sonarr.url if self.config.sonarr else "",
                    }
                    content = template.render(**context)

                    # Write file
                    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
                    filename = f"{safe_title} ({year or 'Unknown'}).md"
                    path = self.vault_path / "Series" / filename
                    if self._write_note(path, content, dry_run):
                        stats["created"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing series from Sonarr: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch series from Sonarr: {e}")
            stats["errors"] += 1

        return stats

    def sync_radarr(self, dry_run: bool = False) -> Dict[str, int]:
        """Sync movies from Radarr to Obsidian."""
        if not self.radarr_client:
            raise ValueError("Radarr client not configured")
        if not self.vault_path:
            raise ValueError("Obsidian vault not configured")

        stats = {"movies": 0, "created": 0, "skipped": 0, "errors": 0}
        try:
            movies = self.radarr_client.get_movies()
            stats["movies"] = len(movies)
            for movie in movies:
                try:
                    # Radarr movie dict fields: id, title, year, genres, ratings
                    movie_id = movie.get("id")
                    title = movie.get("title", "Unknown")
                    year = movie.get("year") or movie.get("releaseDate", "")[:4] if movie.get("releaseDate") else ""
                    # genres might be list of strings
                    genres_raw = movie.get("genres", [])
                    genres = [g if isinstance(g, str) else g.get("name", "") for g in genres_raw if g]
                    # rating
                    rating = None
                    ratings = movie.get("ratings", {})
                    if ratings:
                        rating = ratings.get("CommunityRating") or ratings.get("value")
                        if rating:
                            rating = float(rating)

                    # Render note
                    template = self._get_template("movie")
                    context = {
                        "title": title,
                        "year": year,
                        "rating": rating or "",
                        "watched_date": "",  # Radarr doesn't track watched; can add manually
                        "genres": genres,
                        "jellyfin_id": None,
                        "jellyfin_url": "",
                        "sonarr_id": None,
                        "sonarr_url": "",
                        "radarr_id": movie_id,
                        "radarr_url": self.config.radarr.url if self.config.radarr else "",
                    }
                    content = template.render(**context)

                    # Write file
                    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
                    filename = f"{safe_title} ({year or 'Unknown'}).md"
                    path = self.vault_path / "Movies" / filename
                    if self._write_note(path, content, dry_run):
                        stats["created"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing movie from Radarr: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch movies from Radarr: {e}")
            stats["errors"] += 1

        return stats

    def sync_all(self, dry_run: bool = False) -> Dict[str, Dict[str, int]]:
        """Run all configured syncs."""
        results = {}
        if self.jellyfin_client:
            results["jellyfin"] = self.sync_jellyfin(dry_run=dry_run)
        if self.sonarr_client:
            results["sonarr"] = self.sync_sonarr(dry_run=dry_run)
        if self.radarr_client:
            results["radarr"] = self.sync_radarr(dry_run=dry_run)
        return results
