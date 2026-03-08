"""Configuration loading from YAML and environment variables."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, field_validator

from .config import JellyfinConfig, ObsidianConfig, MediaSyncConfig


class ConfigLoader:
    """Load configuration from file and/or environment."""

    @staticmethod
    def load_yaml(path: Path) -> dict:
        """Load YAML file."""
        if not path.exists():
            return {}
        with open(path) as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def merge_env(config: dict) -> dict:
        """Override config with environment variables."""
        env_map = {
            "JELLYFIN_URL": ("jellyfin", "url"),
            "JELLYFIN_API_KEY": ("jellyfin", "api_key"),
            "OBSIDIAN_VAULT": ("obsidian", "vault_path"),
            "OBSIDIAN_TEMPLATE": ("obsidian", "template"),
            "SONARR_URL": ("sonarr", "url"),
            "SONARR_API_KEY": ("sonarr", "api_key"),
            "RADARR_URL": ("radarr", "url"),
            "RADARR_API_KEY": ("radarr", "api_key"),
        }
        for env_var, (section, key) in env_map.items():
            val = os.getenv(env_var)
            if val:
                config.setdefault(section, {})[key] = val
        return config

    def load(self, config_path: Optional[Path] = None) -> MediaSyncConfig:
        """Load configuration from default or specified path."""
        if config_path is None:
            config_path = Path.home() / ".config" / "media-sync" / "config.yaml"
        raw = self.load_yaml(config_path)
        raw = self.merge_env(raw)
        return MediaSyncConfig.from_yaml(raw)