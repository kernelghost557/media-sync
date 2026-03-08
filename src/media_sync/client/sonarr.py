"""Sonarr API client."""

import logging
from typing import Any

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class SonarrClient(BaseAPIClient):
    """Client for Sonarr REST API."""

    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)
        # Sonarr uses X-Api-Key header
        self.session.headers.update({"X-Api-Key": api_key})

    def get_series(self) -> list[dict]:
        """Fetch all series."""
        return self.get("/api/v3/series")

    def get_episodes(self, series_id: int, season_number: int = None) -> list[dict]:
        """Fetch episodes for a series. Optionally filter by season."""
        params = {"seriesId": series_id}
        if season_number is not None:
            params["seasonNumber"] = season_number
        return self.get("/api/v3/episode", params=params)

    def get_commands(self, command_id: int = None) -> list[dict]:
        """Get command info."""
        if command_id:
            return self.get(f"/api/v3/command/{command_id}")
        return self.get("/api/v3/command")

    def refresh_series(self, series_ids: list[int] = None) -> dict:
        """Refresh series metadata."""
        payload = {"name": "RefreshSeries"}
        if series_ids:
            payload["seriesIds"] = series_ids
        return self.post("/api/v3/command", json=payload)

    def search_episodes(self, episode_ids: list[int]) -> dict:
        """Search for missing episodes (trigger download)."""
        payload = {"name": "EpisodeSearch", "episodeIds": episode_ids}
        return self.post("/api/v3/command", json=payload)

    def get_series_by_name(self, title: str) -> list[dict]:
        """Find series by title (case-insensitive partial match)."""
        all_series = self.get_series()
        title_lower = title.lower()
        matches = [s for s in all_series if title_lower in s.get("title", "").lower()]
        return matches

    def get_episode_file(self, episode_id: int) -> dict:
        """Get file info for an episode."""
        return self.get(f"/api/v3/episodeFile/{episode_id}")

    def delete_episode_file(self, episode_file_id: int) -> bool:
        """Delete episode file (unmonitor)."""
        self.session.delete(f"{self.base_url}/api/v3/episodeFile/{episode_file_id}", headers=self.session.headers)
        return True

    def healthcheck(self) -> dict[str, Any]:
        """Check Sonarr health."""
        try:
            system = self.get("/api/v3/system/status")
            return {"status": "ok", "version": system.get("version"), "os": system.get("osName")}
        except Exception as e:
            return {"status": "error", "error": str(e)}