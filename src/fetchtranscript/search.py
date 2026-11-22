"""Search API module."""

from __future__ import annotations

from typing import Any


class SearchAPI:
    """Sync search API."""

    def __init__(self, client: Any):
        self._client = client

    def videos(self, query: str, limit: int = 10) -> dict[str, Any]:
        """
        Search for YouTube videos.

        Args:
            query: Search query string
            limit: Maximum number of results (1-50, default: 10)

        Returns:
            Dict with query, results list, and total_results.
        """
        params: dict[str, Any] = {"q": query}
        if limit != 10:
            params["limit"] = limit
        return self._client._request("GET", "/v1/search", params=params)

    def find_videos_with_transcripts(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Search for videos and check transcript availability.

        Note: Makes multiple API calls (1 search + N language checks).

        Args:
            query: Search query string
            limit: Maximum number of results to check

        Returns:
            List of video dicts with has_transcript and available_languages fields.
        """
        results = self.videos(query, limit=limit)
        videos_with_info = []

        for video in results.get("results", []):
            video_copy = dict(video)
            try:
                languages = self._client.transcripts.list_languages(video["video_id"])
                video_copy["has_transcript"] = len(languages.get("languages", [])) > 0
                video_copy["available_languages"] = [
                    lang["language_code"] for lang in languages.get("languages", [])
                ]
            except Exception:
                video_copy["has_transcript"] = False
                video_copy["available_languages"] = []
            videos_with_info.append(video_copy)

        return videos_with_info


class AsyncSearchAPI:
    """Async search API."""

    def __init__(self, client: Any):
        self._client = client

    async def videos(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search for YouTube videos."""
        params: dict[str, Any] = {"q": query}
        if limit != 10:
            params["limit"] = limit
        return await self._client._request("GET", "/v1/search", params=params)

    async def find_videos_with_transcripts(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search for videos and check transcript availability."""
        results = await self.videos(query, limit=limit)
        videos_with_info = []

        for video in results.get("results", []):
            video_copy = dict(video)
            try:
                languages = await self._client.transcripts.list_languages(video["video_id"])
                video_copy["has_transcript"] = len(languages.get("languages", [])) > 0
                video_copy["available_languages"] = [
                    lang["language_code"] for lang in languages.get("languages", [])
                ]
            except Exception:
                video_copy["has_transcript"] = False
                video_copy["available_languages"] = []
            videos_with_info.append(video_copy)

        return videos_with_info
