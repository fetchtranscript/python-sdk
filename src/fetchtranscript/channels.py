"""Channels API module."""

from __future__ import annotations

from typing import Any

# Largest page the API serves (GET /v1/channels/{id}/videos?limit=1-100); 1 credit per page.
MAX_PAGE_SIZE = 100


class ChannelsAPI:
    """Sync channels API."""

    def __init__(self, client: Any):
        self._client = client

    def get_info(self, channel_id: str) -> dict[str, Any]:
        """
        Get information about a YouTube channel.

        Args:
            channel_id: YouTube channel ID (UC...) or handle (@...)

        Returns:
            Dict with channel metadata.
        """
        return self._client._request("GET", f"/v1/channels/{channel_id}")

    def get_videos(
        self,
        channel_id: str,
        limit: int = 30,
        offset: int = 0,
        include_shorts: bool = False,
    ) -> dict[str, Any]:
        """
        Get videos from a YouTube channel (1 credit per call).

        Args:
            channel_id: YouTube channel ID (UC...) or handle (@...)
            limit: Maximum number of videos (1-100, default: 30)
            offset: Number of videos to skip for pagination
            include_shorts: Whether to include YouTube Shorts (default: False). With
                Shorts the whole channel is listed by view count, which is slower.

        Returns:
            Dict with videos list, total_count, and has_more.
        """
        params = _build_videos_params(limit, offset, include_shorts)
        return self._client._request("GET", f"/v1/channels/{channel_id}/videos", params=params)

    def get_all_videos(
        self,
        channel_id: str,
        include_shorts: bool = False,
        max_videos: int = 500,
    ) -> list[dict[str, Any]]:
        """
        Get all videos from a channel with automatic pagination (1 credit per page of 100).

        Args:
            channel_id: YouTube channel ID (UC...) or handle (@...)
            include_shorts: Whether to include YouTube Shorts (default: False)
            max_videos: Maximum total videos to fetch (default: 500)

        Returns:
            List of video dicts.
        """
        all_videos: list[dict[str, Any]] = []
        offset = 0
        limit = MAX_PAGE_SIZE

        while len(all_videos) < max_videos:
            result = self.get_videos(
                channel_id,
                limit=min(limit, max_videos - len(all_videos)),
                offset=offset,
                include_shorts=include_shorts,
            )
            videos = result.get("videos", [])
            all_videos.extend(videos)
            if not result.get("has_more") or not videos:
                break
            offset += len(videos)

        return all_videos


class AsyncChannelsAPI:
    """Async channels API."""

    def __init__(self, client: Any):
        self._client = client

    async def get_info(self, channel_id: str) -> dict[str, Any]:
        """Get information about a YouTube channel."""
        return await self._client._request("GET", f"/v1/channels/{channel_id}")

    async def get_videos(
        self,
        channel_id: str,
        limit: int = 30,
        offset: int = 0,
        include_shorts: bool = False,
    ) -> dict[str, Any]:
        """Get videos from a YouTube channel (see ChannelsAPI.get_videos)."""
        params = _build_videos_params(limit, offset, include_shorts)
        return await self._client._request(
            "GET", f"/v1/channels/{channel_id}/videos", params=params
        )

    async def get_all_videos(
        self,
        channel_id: str,
        include_shorts: bool = False,
        max_videos: int = 500,
    ) -> list[dict[str, Any]]:
        """Get all videos from a channel with automatic pagination."""
        all_videos: list[dict[str, Any]] = []
        offset = 0
        limit = MAX_PAGE_SIZE

        while len(all_videos) < max_videos:
            result = await self.get_videos(
                channel_id,
                limit=min(limit, max_videos - len(all_videos)),
                offset=offset,
                include_shorts=include_shorts,
            )
            videos = result.get("videos", [])
            all_videos.extend(videos)
            if not result.get("has_more") or not videos:
                break
            offset += len(videos)

        return all_videos


def _build_videos_params(limit: int, offset: int, include_shorts: bool) -> dict[str, Any]:
    """Always send every parameter: the API has its own defaults (limit 30, no Shorts), so
    leaving one out made the SDK's value silently not apply."""
    return {
        "limit": limit,
        "offset": offset,
        "include_shorts": "true" if include_shorts else "false",
    }
