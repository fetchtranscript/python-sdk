"""Asynchronous FetchTranscript client."""

from __future__ import annotations

from typing import Any

import httpx

from ._base import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, build_headers
from .errors import raise_for_status
from .transcripts import AsyncTranscriptsAPI
from .videos import AsyncVideosAPI
from .channels import AsyncChannelsAPI
from .search import AsyncSearchAPI


class AsyncFetchTranscriptClient:
    """
    Asynchronous client for the FetchTranscript API.

    Usage:
        async with AsyncFetchTranscriptClient(api_key="yt_xxx") as client:
            transcript = await client.transcripts.get("dQw4w9WgXcQ")
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

        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers=build_headers(self.api_key),
            timeout=timeout,
        )

        self.transcripts = AsyncTranscriptsAPI(self)
        self.videos = AsyncVideosAPI(self)
        self.channels = AsyncChannelsAPI(self)
        self.search = AsyncSearchAPI(self)

        self._last_response: httpx.Response | None = None

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make an async HTTP request to the API."""
        response = await self._http.request(method, path, params=params, **kwargs)
        self._last_response = response
        raise_for_status(response)
        return response.json()

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request."""
        return await self._request("GET", path, params=params)

    async def post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a POST request."""
        return await self._request("POST", path, json=data)

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

    async def health_check(self) -> dict[str, Any]:
        """Check API health status."""
        response = await self._http.get("/health")
        return response.json()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    async def __aenter__(self) -> AsyncFetchTranscriptClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
