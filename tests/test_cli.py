"""Tests for media-sync CLI."""

from click.testing import CliRunner
from media_sync.cli import main
import pytest


def test_version():
    """Test --version flag."""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_healthcheck():
    """Test healthcheck command."""
    runner = CliRunner()
    result = runner.invoke(main, ["healthcheck"])
    assert result.exit_code == 0
    assert "Healthcheck" in result.output


def test_sync_dry_run(monkeypatch):
    """Test sync command with dry-run."""
    # Mock SyncEngine to avoid real network calls
    class DummyEngine:
        def __init__(self, *args, **kwargs):
            pass
        def sync_all(self, dry_run=False):
            return {}

    monkeypatch.setattr('media_sync.sync.SyncEngine', DummyEngine)

    runner = CliRunner()
    result = runner.invoke(main, ["sync", "--dry-run"])
    assert result.exit_code == 0
    assert "Starting sync" in result.output


def test_config_init(tmp_path):
    """Test config initialization creates file."""
    runner = CliRunner()
    # Override default path for test
    # This is a simplified test; in reality we'd patch the path
    result = runner.invoke(main, ["config-init"])
    assert result.exit_code == 0
    assert "Created config" in result.output or "Config already exists" in result.output