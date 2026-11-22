"""Synchronous FetchTranscript client."""

from __future__ import annotations

from typing import Any

import httpx

from ._base import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, build_headers
from .errors import raise_for_status
from .transcripts import TranscriptsAPI
from .videos import VideosAPI
from .channels import ChannelsAPI
from .search import SearchAPI


class FetchTranscriptClient:
    """
    Synchronous client for the FetchTranscript API.

    Usage:
        client = FetchTranscriptClient(api_key="yt_xxx")
        transcript = client.transcripts.get("dQw4w9WgXcQ")

        # Or as context manager
        with FetchTranscriptClient(api_key="yt_xxx") as client:
            transcript = client.transcripts.get("dQw4w9WgXcQ")
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._http = httpx.Client(
            base_url=self.base_url,
            headers=build_headers(self.api_key),
            timeout=timeout,
        )

        self.transcripts = TranscriptsAPI(self)
        self.videos = VideosAPI(self)
        self.channels = ChannelsAPI(self)
        self.search = SearchAPI(self)

        self._last_response: httpx.Response | None = None

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API."""
        response = self._http.request(method, path, params=params, **kwargs)
        self._last_response = response
        raise_for_status(response)
        return response.json()

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path, params=params)

    def post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, json=data)

    @property
    def credits_remaining(self) -> int | None:
        """Get remaining credits from the last response."""
        if self._last_response is not None:
            value = self._last_response.headers.get("x-credits-remaining")
            return int(value) if value else None
        return None

    @property
    def processing_time_ms(self) -> int | None:
        """Get processing time in ms from the last response."""
        if self._last_response is not None:
            value = self._last_response.headers.get("x-processing-time")
            return int(value) if value else None
        return None

    def health_check(self) -> dict[str, Any]:
        """Check API health status."""
        response = self._http.get("/health")
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self) -> FetchTranscriptClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
