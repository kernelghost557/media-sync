"""Synchronization engine: Jellyfin/Sonarr/Radarr -> Obsidian."""

import logging
from pathlib import Path

from .config_loader import ConfigLoader
from .client.jellyfin import JellyfinClient
from .client.sonarr import SonarrClient
from .client.radarr import RadarrClient
from .obsidian import ObsidianGenerator
from .models.media import Movie, Series
# We'll adapt Sonarr/Radarr models to our internal ones

logger = logging.getLogger(__name__)


class SyncEngine:
    """Multi-source sync to Obsidian."""

    def __init__(self, config_loader: ConfigLoader):
        self.config = config_loader.load()
        self.jellyfin = None
        self.sonarr = None
        self.radarr = None
        self.obsidian = None

        if self.config.jellyfin:
            self.jellyfin = JellyfinClient(
                base_url=self.config.jellyfin.url,
                api_key=self.config.jellyfin.api_key,
            )
        if self.config.sonarr:
            self.sonarr = SonarrClient(
                base_url=self.config.sonarr.url,
                api_key=self.config.sonarr.api_key,
            )
        if self.config.radarr:
            self.radarr = RadarrClient(
                base_url=self.config.radarr.url,
                api_key=self.config.radarr.api_key,
            )
        if self.config.obsidian:
            self.obsidian = ObsidianGenerator(
                vault_path=self.config.obsidian.vault_path,
                template_path=self.config.obsidian.template,
            )
        else:
            raise ValueError("Obsidian configuration is missing")

    def sync_jellyfin(self, dry_run: bool = False) -> dict:
        """Sync Jellyfin movies and series."""
        stats = {"movies": 0, "series": 0, "created": 0, "skipped": 0, "errors": 0}
        try:
            movies = self.jellyfin.get_movies()
            stats["movies"] = len(movies)
            for movie in movies:
                try:
                    if dry_run:
                        logger.info(f"[DRY] Would create note for movie: {movie.name}")
                        stats["created"] += 1
                    else:
                        note = self.obsidian.generate_note(movie, overwrite=False)
                        if note:
                            stats["created"] += 1
                        else:
                            stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing movie {movie.name}: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch movies from Jellyfin: {e}")
            stats["errors"] += 1

        try:
            series_list = self.jellyfin.get_series()
            stats["series"] = len(series_list)
            for series in series_list:
                try:
                    if dry_run:
                        logger.info(f"[DRY] Would create note for series: {series.name}")
                        stats["created"] += 1
                    else:
                        note = self.obsidian.generate_note(series, overwrite=False)
                        if note:
                            stats["created"] += 1
                        else:
                            stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing series {series.name}: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch series from Jellyfin: {e}")
            stats["errors"] += 1

        return stats

    def sync_sonarr(self, dry_run: bool = False) -> dict:
        """Sync series from Sonarr to Obsidian."""
        stats = {"series": 0, "created": 0, "skipped": 0, "errors": 0}
        if not self.sonarr:
            logger.warning("Sonarr not configured")
            return stats

        try:
            series_list = self.sonarr.get_series()
            stats["series"] = len(series_list)
            for series in series_list:
                try:
                    # Map Sonarr series to our Series model
                    s = Series(
                        id=str(series["id"]),
                        name=series["title"],
                        original_title=series.get("originalTitle"),
                        year=series.get("year"),
                        overview=series.get("overview"),
                        genre=series.get("genres", []),
                        season_count=series.get("seasonCount"),
                        episode_count=series.get("totalEpisodeCount"),
                        status=series.get("status"),
                        production_year=series.get("year"),
                    )
                    if dry_run:
                        logger.info(f"[DRY] Would create note for Sonarr series: {s.name}")
                        stats["created"] += 1
                    else:
                        note = self.obsidian.generate_note(s, overwrite=False)
                        if note:
                            stats["created"] += 1
                        else:
                            stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing Sonarr series {series.get('title')}: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch series from Sonarr: {e}")
            stats["errors"] += 1

        return stats

    def sync_radarr(self, dry_run: bool = False) -> dict:
        """Sync movies from Radarr to Obsidian."""
        stats = {"movies": 0, "created": 0, "skipped": 0, "errors": 0}
        if not self.radarr:
            logger.warning("Radarr not configured")
            return stats

        try:
            movies = self.radarr.get_movies()
            stats["movies"] = len(movies)
            for movie in movies:
                try:
                    m = Movie(
                        id=str(movie["id"]),
                        name=movie["title"],
                        original_title=movie.get("originalTitle"),
                        year=movie.get("year"),
                        overview=movie.get("overview"),
                        genre=movie.get("genres", []),
                        community_rating=movie.get("ratings", {}).get("value"),
                        official_rating=movie.get("contentRating"),
                        production_year=movie.get("year"),
                    )
                    if dry_run:
                        logger.info(f"[DRY] Would create note for Radarr movie: {m.name}")
                        stats["created"] += 1
                    else:
                        note = self.obsidian.generate_note(m, overwrite=False)
                        if note:
                            stats["created"] += 1
                        else:
                            stats["skipped"] += 1
                except Exception as e:
                    logger.error(f"Error processing Radarr movie {movie.get('title')}: {e}")
                    stats["errors"] += 1
        except Exception as e:
            logger.error(f"Failed to fetch movies from Radarr: {e}")
            stats["errors"] += 1

        return stats

    def sync_all(self, dry_run: bool = False) -> dict:
        """Sync all configured sources to Obsidian."""
        total_stats = {"jellyfin": {}, "sonarr": {}, "radarr": {}}
        if self.jellyfin:
            total_stats["jellyfin"] = self.sync_jellyfin(dry_run=dry_run)
        if self.sonarr:
            total_stats["sonarr"] = self.sync_sonarr(dry_run=dry_run)
        if self.radarr:
            total_stats["radarr"] = self.sync_radarr(dry_run=dry_run)
        return total_stats