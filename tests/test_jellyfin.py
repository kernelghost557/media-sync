"""Tests for Jellyfin API client."""

import pytest
from unittest.mock import Mock, patch
from media_sync.client.jellyfin import JellyfinClient
from media_sync.models.media import Movie, Series


@pytest.fixture
def mock_session():
    """Mock requests.Session."""
    with patch("media_sync.client.base.requests.Session") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        yield mock_session


def test_jellyfin_client_initialization(mock_session):
    """Test client setup with explicit user_id."""
    mock_response = Mock()
    mock_response.json.return_value = {"Id": "user123", "Name": "testuser"}
    mock_session.request.return_value = mock_response

    client = JellyfinClient("http://localhost:8096", "apikey", user_id="explicit123")
    assert client.user_id == "explicit123"


def test_jellyfin_client_fetches_user_id(mock_session):
    """Test client fetches user ID when not provided."""
    mock_response = Mock()
    mock_response.json.return_value = {"Id": "auto_user", "Name": "auto"}
    mock_session.request.return_value = mock_response

    client = JellyfinClient("http://localhost:8096", "apikey")
    assert client.user_id == "auto_user"


def test_get_movies_parses_response(mock_session):
    """Test get_movies returns list of Movie objects."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "Items": [
            {
                "Id": "movie1",
                "Name": "Test Movie",
                "OriginalTitle": "Original Title",
                "ProductionYear": 2020,
                "RunTimeTicks": 72000000000,  # 2 minutes in ticks (approx)
                "Genres": ["Action", "Sci-Fi"],
                "CommunityRating": 8.5,
                "Tags": ["4K", "favorite"],
            }
        ]
    }
    mock_session.request.return_value = mock_response

    client = JellyfinClient("http://localhost:8096", "apikey", user_id="u123")
    movies = client.get_movies()

    assert len(movies) == 1
    assert isinstance(movies[0], Movie)
    assert movies[0].id == "movie1"
    assert movies[0].name == "Test Movie"
    assert movies[0].duration_minutes == 2


def test_get_series_parses_response(mock_session):
    """Test get_series returns list of Series objects."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "Items": [
            {
                "Id": "series1",
                "Name": "Test Series",
                "ProductionYear": 2019,
                "Status": "Continuing",
                "SeasonCount": 3,
                "EpisodeCount": 30,
                "Genres": ["Drama"],
            }
        ]
    }
    mock_session.request.return_value = mock_response

    client = JellyfinClient("http://localhost:8096", "apikey", user_id="u123")
    series_list = client.get_series()

    assert len(series_list) == 1
    s = series_list[0]
    assert isinstance(s, Series)
    assert s.status == "Continuing"
    assert s.season_count == 3
    assert s.total_episodes == "30 episodes"


def test_mark_as_played_sends_post(mock_session):
    """Test mark_as_played sends correct POST request."""
    mock_response = Mock()
    mock_response.status_code = 204
    mock_session.request.return_value = mock_response

    client = JellyfinClient("http://localhost:8096", "apikey", user_id="u123")
    result = client.mark_as_played("item123")

    assert result is True
    mock_session.request.assert_called_once()
    args, kwargs = mock_session.request.call_args
    assert args[0] == "POST"
    assert "/Users/u123/PlayedItems/item123" in args[1]