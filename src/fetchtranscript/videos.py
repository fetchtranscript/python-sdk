"""Videos API module."""

from __future__ import annotations

from typing import Any


class VideosAPI:
    """Sync videos API."""

    def __init__(self, client: Any):
        self._client = client

    def get_metadata(self, video_id: str) -> dict[str, Any]:
        """
        Get metadata for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with video metadata (title, description, view_count, etc.)
        """
        return self._client._request("GET", f"/v1/videos/{video_id}")

    def get_chapters(self, video_id: str) -> dict[str, Any]:
        """
        Get chapters for a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with chapters list and has_chapters flag.
        """
        return self._client._request("GET", f"/v1/videos/{video_id}/chapters")

    def get_comments(self, video_id: str, limit: int = 100, sort: str = "top") -> dict[str, Any]:
        """
        Get the top-level comments of a YouTube video.

        Costs 1 credit per 100 comments returned, rounded up (minimum 1). If your balance
        pays for fewer than `limit` comments, you get as many as it pays for and has_more
        is true. Videos with comments turned off raise an error and cost nothing.

        Args:
            video_id: YouTube video ID
            limit: Maximum number of comments (1-500, default: 100)
            sort: "top" (default) or "new" (newest first)

        Returns:
            Dict with comments list, total_count (the video's comment count as YouTube
            shows it, replies included), and has_more.
        """
        params = {"limit": limit, "sort": sort}
        return self._client._request("GET", f"/v1/videos/{video_id}/comments", params=params)


class AsyncVideosAPI:
    """Async videos API."""

    def __init__(self, client: Any):
        self._client = client

    async def get_metadata(self, video_id: str) -> dict[str, Any]:
        """Get metadata for a YouTube video."""
        return await self._client._request("GET", f"/v1/videos/{video_id}")

    async def get_chapters(self, video_id: str) -> dict[str, Any]:
        """Get chapters for a YouTube video."""
        return await self._client._request("GET", f"/v1/videos/{video_id}/chapters")

    async def get_comments(
        self, video_id: str, limit: int = 100, sort: str = "top"
    ) -> dict[str, Any]:
        """Get the top-level comments of a YouTube video (see VideosAPI.get_comments).

        Costs 1 credit per 100 comments returned, rounded up (minimum 1).
        """
        params = {"limit": limit, "sort": sort}
        return await self._client._request("GET", f"/v1/videos/{video_id}/comments", params=params)
