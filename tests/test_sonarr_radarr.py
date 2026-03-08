"""Tests for Sonarr and Radarr clients."""

from unittest.mock import Mock, patch
from media_sync.client.sonarr import SonarrClient
from media_sync.client.radarr import RadarrClient


def test_sonarr_get_series(mock_requests):
    # mock_requests от pytest mock будет заменять requests.Session
    # Но мы используем BaseAPIClient, который использует requests.Session напрямую
    with patch("media_sync.client.base.requests.Session") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = [{"id": 1, "title": "Test Series"}]
        mock_session.request.return_value = mock_response

        client = SonarrClient("http://localhost:8989", "apikey")
        series = client.get_series()
        assert len(series) == 1
        assert series[0]["title"] == "Test Series"


def test_sonarr_healthcheck(mock_requests):
    with patch("media_sync.client.base.requests.Session") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = {"version": "3.0.9", "osName": "Linux"}
        mock_session.request.return_value = mock_response

        client = SonarrClient("http://localhost:8989", "apikey")
        health = client.healthcheck()
        assert health["status"] == "ok"
        assert health["version"] == "3.0.9"


def test_radarr_get_movies(mock_requests):
    with patch("media_sync.client.base.requests.Session") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = [
            {"id": 1, "title": "Test Movie", "year": 2020, "genres": ["Action"]}
        ]
        mock_session.request.return_value = mock_response

        client = RadarrClient("http://localhost:7878", "apikey")
        movies = client.get_movies()
        assert len(movies) == 1
        assert movies[0]["title"] == "Test Movie"


def test_radarr_healthcheck(mock_requests):
    with patch("media_sync.client.base.requests.Session") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_response = Mock()
        mock_response.json.return_value = {"version": "3.0.6", "osName": "Linux"}
        mock_session.request.return_value = mock_response

        client = RadarrClient("http://localhost:7878", "apikey")
        health = client.healthcheck()
        assert health["status"] == "ok"