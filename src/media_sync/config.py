"""Configuration models for media-sync."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class JellyfinConfig(BaseModel):
    """Jellyfin connection configuration."""

    url: str = Field(..., description="Base URL of Jellyfin server")
    api_key: str = Field(..., description="API key for authentication")
    username: Optional[str] = Field(None, description="User identifier (optional)")

    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        """Remove trailing slash from URL."""
        return v.rstrip("/")


class ObsidianConfig(BaseModel):
    """Obsidian vault configuration."""

    vault_path: Path = Field(..., description="Path to Obsidian vault directory")
    template: Optional[Path] = Field(None, description="Path to note template file")

    @field_validator("vault_path")
    @classmethod
    def expand_path(cls, v: Path) -> Path:
        """Expand user home directory."""
        return v.expanduser().resolve()

    @field_validator("template")
    @classmethod
    def expand_template(cls, v: Optional[Path]) -> Optional[Path]:
        """Expand template path if provided."""
        if v:
            return v.expanduser().resolve()
        return v


class MediaSyncConfig(BaseModel):
    """Main configuration container."""

    jellyfin: Optional[JellyfinConfig] = None
    obsidian: Optional[ObsidianConfig] = None

    @classmethod
    def from_yaml(cls, data: dict) -> "MediaSyncConfig":
        """Create config from YAML dictionary."""
        # Will be implemented when we load YAML
        raise NotImplementedError