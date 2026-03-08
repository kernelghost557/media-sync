"""Tests for configuration loading with Sonarr/Radarr."""

import tempfile
from pathlib import Path

import pytest

from media_sync.config_loader import ConfigLoader
from media_sync.config import SonarrConfig, RadarrConfig


def test_load_config_with_sonarr_radarr(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
jellyfin:
  url: "http://localhost:8096"
  api_key: "jellykey"
sonarr:
  url: "http://localhost:8989"
  api_key: "sonarrkey"
radarr:
  url: "http://localhost:7878"
  api_key: "radarrkey"
obsidian:
  vault_path: "/home/user/vault"
""")
    loader = ConfigLoader()
    config = loader.load(config_file)
    assert isinstance(config.sonarr, SonarrConfig)
    assert config.sonarr.url == "http://localhost:8989"
    assert config.sonarr.api_key == "sonarrkey"
    assert isinstance(config.radarr, RadarrConfig)
    assert config.radarr.url == "http://localhost:7878"
    assert config.radarr.api_key == "radarrkey"


def test_merge_env_sonarr_radarr(monkeypatch):
    loader = ConfigLoader()
    raw = {"sonarr": {"url": "http://localhost:8989"}}
    monkeypatch.setenv("SONARR_API_KEY", "secret-sonarr")
    monkeypatch.setenv("RADARR_URL", "http://new-radarr:7878")
    merged = loader.merge_env(raw)
    assert merged["sonarr"]["api_key"] == "secret-sonarr"
    assert "radarr" in merged
    assert merged["radarr"]["url"] == "http://new-radarr:7878"