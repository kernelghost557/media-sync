"""Radarr API client."""

import logging
from typing import Any

from .base import BaseAPIClient

logger = logging.getLogger(__name__)


class RadarrClient(BaseAPIClient):
    """Client for Radarr REST API."""

    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url, api_key)
        # Radarr uses X-Api-Key header
        self.session.headers.update({"X-Api-Key": api_key})

    def get_movies(self) -> list[dict]:
        """Fetch all movies."""
        return self.get("/api/v3/movie")

    def get_movie(self, movie_id: int) -> dict:
        """Get movie by ID."""
        return self.get(f"/api/v3/movie/{movie_id}")

    def refresh_movie(self, movie_ids: list[int] = None) -> dict:
        """Refresh movie metadata."""
        payload = {"name": "RefreshMovie"}
        if movie_ids:
            payload["movieIds"] = movie_ids
        return self.post("/api/v3/command", json=payload)

    def search_movies(self, query: str) -> list[dict]:
        """Search for movies by title."""
        params = {"query": query}
        return self.get("/api/v3/movie/lookup", params=params)

    def get_commands(self, command_id: int = None) -> list[dict]:
        """Get command info."""
        if command_id:
            return self.get(f"/api/v3/command/{command_id}")
        return self.get("/api/v3/command")

    def healthcheck(self) -> dict[str, Any]:
        """Check Radarr health."""
        try:
            system = self.get("/api/v3/system/status")
            return {"status": "ok", "version": system.get("version"), "os": system.get("osName")}
        except Exception as e:
            return {"status": "error", "error": str(e)}