"""Jellyfin API client using httpx."""

import logging
import time
from typing import Any, Optional

import httpx

from ..models.media import Movie, Series, Episode

logger = logging.getLogger(__name__)


class JellyfinClient:
    """Client for Jellyfin REST API using httpx."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        user_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize Jellyfin client.

        Args:
            base_url: Jellyfin server URL (e.g., http://localhost:8096)
            api_key: API key for authentication
            user_id: Optional user ID. If None, will fetch from /Users/me
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_id = user_id

        # Configure headers
        headers = {"X-MediaBrowser-Token": api_key} if api_key else {}

        # Create httpx client
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

        if not self.user_id:
            self.user_id = self._get_current_user_id()

    def _get_current_user_id(self) -> str:
        """Fetch the current user's ID."""
        data = self._request("GET", "/Users/me")
        user_id = data.get("Id")
        if not user_id:
            raise ValueError("Could not determine user ID from Jellyfin")
        logger.info(f"Authenticated as user: {data.get('Name')} ({user_id})")
        return user_id

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        for attempt in range(self.max_retries):
            try:
                response = self._client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                # Return JSON if content exists, else None
                return response.json() if response.content else None
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning(
                    f"Request failed (attempt {attempt+1}/{self.max_retries}): {method} {url} - {e}"
                )
                if attempt == self.max_retries - 1:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    raise
                # Exponential backoff
                time.sleep(2**attempt)

    def get(self, endpoint: str, **kwargs: Any) -> Any:
        """GET request."""
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> Any:
        """POST request."""
        return self._request("POST", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """DELETE request."""
        return self._request("DELETE", endpoint, **kwargs)

    # -------------------- Library & Items --------------------

    def get_movies(self, include_favorite: bool = False) -> list[Movie]:
        """Fetch all movies from the library."""
        params = {
            "IncludeItemTypes": "Movie",
            "Recursive": "true",
            "fields": "DateCreated,CommunityRating,OfficialRating,Path,RunTimeTicks,ProductionYear,Genres,Tags,Taglines,Overview,OriginalTitle,Taglines,People",
            "SortBy": "SortName",
            "SortOrder": "Ascending",
        }
        if include_favorite:
            params["IsFavorite"] = "true"

        # Pagination
        start_index = 0
        page_limit = 100
        all_items = []
        while True:
            params["StartIndex"] = start_index
            params["Limit"] = page_limit
            data = self.get(f"/Users/{self.user_id}/Items", params=params)
            items = data.get("Items", [])
            if not items:
                break
            all_items.extend(items)
            if len(items) < page_limit:
                break
            start_index += len(items)

        return [Movie(**item) for item in all_items]

    def get_series(self) -> list[Series]:
        """Fetch all TV series."""
        params = {
            "IncludeItemTypes": "Series",
            "Recursive": "true",
            "fields": "DateCreated,CommunityRating,OfficialRating,Path,RunTimeTicks,ProductionYear,Genres,Tags,Taglines,Overview,OriginalTitle,People,SeasonCount,EpisodeCount,Status",
        }

        start_index = 0
        page_limit = 100
        all_items = []
        while True:
            params["StartIndex"] = start_index
            params["Limit"] = page_limit
            data = self.get(f"/Users/{self.user_id}/Items", params=params)
            items = data.get("Items", [])
            if not items:
                break
            all_items.extend(items)
            if len(items) < page_limit:
                break
            start_index += len(items)

        return [Series(**item) for item in all_items]

    def get_episodes(self, series_id: str, season_number: int) -> list[Episode]:
        """Fetch episodes for a specific series and season."""
        params = {
            "IncludeItemTypes": "Episode",
            "SeasonId": season_number,
            "fields": "DateCreated,RunTimeTicks,Overview,AirDate,IndexNumber,ParentIndexNumber",
        }
        data = self.get(f"/Users/{self.user_id}/Items", params=params)
        items = data.get("Items", [])
        episodes = []
        for item in items:
            ep = Episode(
                id=item["Id"],
                series_id=series_id,
                season_number=item.get("ParentIndexNumber", 0),
                episode_number=item.get("IndexNumber", 0),
                name=item["Name"],
                overview=item.get("Overview"),
                air_date=item.get("AirDate") or item.get("PremiereDate"),
                run_time_ticks=item.get("RunTimeTicks"),
            )
            episodes.append(ep)
        return episodes

    # -------------------- Playback & Watched Status --------------------

    def mark_as_played(self, item_id: str) -> bool:
        """Mark an item as watched/played."""
        endpoint = f"/Users/{self.user_id}/PlayedItems/{item_id}"
        self.post(endpoint, json={})
        logger.info(f"Marked item {item_id} as played")
        return True

    def mark_as_unplayed(self, item_id: str) -> bool:
        """Mark an item as not watched."""
        endpoint = f"/Users/{self.user_id}/PlayedItems/{item_id}"
        self.delete(endpoint)
        logger.info(f"Marked item {item_id} as not played")
        return True

    def get_playback_info(self, item_id: str) -> dict[str, Any]:
        """Get playback position and last played date for an item."""
        params = {
            "UserId": self.user_id,
            "ItemId": item_id,
        }
        return self.get(f"/Users/{self.user_id}/Items/{item_id}/UserData", params=params)

    # -------------------- User Data (ratings, tags) --------------------

    def set_rating(self, item_id: str, rating: int) -> bool:
        """Set user rating for an item (0-10)."""
        if not 0 <= rating <= 10:
            raise ValueError("Rating must be between 0 and 10")
        endpoint = f"/Users/{self.user_id}/Items/{item_id}/Rating"
        self.post(endpoint, json={"Rating": rating, "ItemId": item_id})
        logger.info(f"Set rating {rating} for item {item_id}")
        return True

    def get_user_data(self, item_id: str) -> dict[str, Any]:
        """Fetch user-specific data: rating, played, likes."""
        return self.get(f"/Users/{self.user_id}/Items/{item_id}/UserData")

    # -------------------- Health & Diagnostics --------------------

    def healthcheck(self) -> dict[str, Any]:
        """Check server health and return basic info."""
        system_info = self.get("/System/Info")
        return {
            "version": system_info.get("Version"),
            "server_name": system_info.get("ServerName"),
            "operating_system": system_info.get("OperatingSystem"),
            "status": "ok",
        }

    def close(self) -> None:
        """Close the underlying HTTP client."""
        try:
            self._client.close()
        except Exception:
            pass
