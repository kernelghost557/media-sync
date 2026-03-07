"""Media Sync - CLI tool for media metadata synchronization."""

__version__ = "0.1.0"

from .cli import main
from .config import JellyfinConfig, ObsidianConfig, MediaSyncConfig
from .models import media as media_models
from .client import jellyfin, base

__all__ = [
    "main",
    "JellyfinConfig",
    "ObsidianConfig",
    "MediaSyncConfig",
    "media_models",
    "jellyfin",
    "base",
]