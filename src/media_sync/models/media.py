"""Models for Jellyfin media items."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MediaItem(BaseModel):
    """Base model for any media item."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: ''.join(word.capitalize() for word in s.split('_'))
    )

    id: str
    name: str
    original_title: Optional[str] = None
    year: Optional[int] = None
    overview: Optional[str] = None
    genres: list[str] = []  # API sends "Genres"
    community_rating: Optional[float] = None
    official_rating: Optional[str] = None
    run_time_ticks: Optional[int] = None  # ticks (100ns per tick)
    production_year: Optional[int] = None
    premiere_date: Optional[str] = None  # ISO date string, API sends "PremiereDate"
    path: Optional[str] = None
    has_icon: bool = False
    has_backdrop: bool = False
    tags: list[str] = []  # user tags, API sends "Tags"

    @property
    def duration_minutes(self) -> Optional[int]:
        """Convert ticks to minutes."""
        if self.run_time_ticks:
            # 1 tick = 100ns = 1e-7 seconds
            return int(self.run_time_ticks * 1e-7 / 60)
        return None

    @property
    def formatted_year(self) -> str:
        """Return year or 'N/A'."""
        return str(self.year) if self.year else "N/A"


class Movie(MediaItem):
    """Movie-specific fields."""

    # Inherits everything; no extra fields yet
    pass


class Series(MediaItem):
    """TV Series-specific fields."""

    season_count: Optional[int] = None
    episode_count: Optional[int] = None
    status: Optional[str] = None  # "Continuing", "Ended", etc.

    @property
    def total_episodes(self) -> str:
        """Display formatted episode count."""
        if self.episode_count:
            return f"{self.episode_count} episodes"
        return "Unknown episodes"


class Episode(BaseModel):
    """Single episode."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda s: ''.join(word.capitalize() for word in s.split('_'))
    )

    id: str
    series_id: str
    season_number: int
    episode_number: int
    name: str
    overview: Optional[str] = None
    air_date: Optional[str] = None  # ISO date, API sends "AirDate"
    run_time_ticks: Optional[int] = None

    @property
    def duration_minutes(self) -> Optional[int]:
        if self.run_time_ticks:
            return int(self.run_time_ticks * 1e-7 / 60)
        return None

    @property
    def full_title(self) -> str:
        """S01E01 - Episode Title"""
        return f"S{self.season_number:02d}E{self.episode_number:02d} - {self.name}"