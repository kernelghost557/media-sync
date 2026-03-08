"""Tests for Obsidian note generator."""

import tempfile
from pathlib import Path

import pytest

from media_sync.obsidian import ObsidianGenerator
from media_sync.models.media import Movie, Series


def test_generate_movie_note(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    gen = ObsidianGenerator(vault_path=vault)
    movie = Movie(
        id="movie123",
        name="Test Movie",
        original_title="Original Title",
        year=2024,
        genre=["Action", "Sci-Fi"],
        community_rating=8.5,
        official_rating="PG-13",
    )
    note = gen.generate_note(movie, overwrite=True)
    assert note is not None
    assert note.exists()
    content = note.read_text()
    assert "Test Movie" in content
    assert "2024" in content
    assert "Action, Sci-Fi" in content
    assert "movie123" in content


def test_generate_series_note(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    gen = ObsidianGenerator(vault_path=vault)
    series = Series(
        id="series123",
        name="Test Series",
        year=2023,
        genre=["Drama"],
        season_count=3,
        episode_count=30,
        status="Continuing",
    )
    note = gen.generate_note(series, overwrite=True)
    assert note is not None
    content = note.read_text()
    assert "Test Series" in content
    assert "series123" in content


def test_sanitize_filename():
    gen = ObsidianGenerator(vault_path=Path("/tmp"))
    bad = 'weird<>:"/\\|?*title'
    good = gen._sanitize_filename(bad)
    assert "<" not in good
    assert " " in good or "_" in good