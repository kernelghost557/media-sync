"""Base HTTP client with retry logic and error handling."""

import logging
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """HTTP client with automatic retries and error handling."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize client with base URL and optional API key."""
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        self.session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        headers = {"Accept": "application/json"}
        if api_key:
            headers["X-MediaBrowser-Token"] = api_key  # Jellyfin header
        self.session.headers.update(headers)

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise

    def get(self, endpoint: str, **kwargs: Any) -> Any:
        """GET request returning JSON."""
        response = self._request("GET", endpoint, **kwargs)
        return response.json() if response.content else None

    def post(self, endpoint: str, **kwargs: Any) -> Any:
        """POST request returning JSON."""
        response = self._request("POST", endpoint, **kwargs)
        return response.json() if response.content else None

    def close(self) -> None:
        """Close session."""
        self.session.close()