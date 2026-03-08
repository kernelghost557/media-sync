"""Tests for configuration loading."""

import tempfile
from pathlib import Path

import pytest

from media_sync.config_loader import ConfigLoader
from media_sync.config import JellyfinConfig, ObsidianConfig


def test_load_yaml_missing(tmp_path: Path):
    loader = ConfigLoader()
    result = loader.load_yaml(tmp_path / "nonexistent.yaml")
    assert result == {}


def test_merge_env(monkeypatch):
    loader = ConfigLoader()
    raw = {"jellyfin": {"url": "http://localhost:8096"}}
    monkeypatch.setenv("JELLYFIN_API_KEY", "secret123")
    merged = loader.merge_env(raw)
    assert merged["jellyfin"]["api_key"] == "secret123"


def test_load_config_from_yaml(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
jellyfin:
  url: "http://localhost:8096"
  api_key: "testkey"
obsidian:
  vault_path: "/home/user/vault"
""")
    loader = ConfigLoader()
    config = loader.load(config_file)
    assert isinstance(config.jellyfin, JellyfinConfig)
    assert config.jellyfin.url == "http://localhost:8096"
    assert config.jellyfin.api_key == "testkey"
    assert isinstance(config.obsidian, ObsidianConfig)
    assert str(config.obsidian.vault_path) == "/home/user/vault"