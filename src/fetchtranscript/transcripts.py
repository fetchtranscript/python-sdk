"""Transcripts API module."""

from __future__ import annotations

from typing import Any, Literal


class TranscriptsAPI:
    """Sync transcripts API."""

    def __init__(self, client: Any):
        self._client = client

    def get(
        self,
        video_id: str,
        lang: str | None = None,
        format: Literal["json", "text", "srt"] = "json",
    ) -> dict[str, Any] | str:
        """
        Get transcript for a YouTube video.

        Args:
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            lang: Language code (e.g., "en", "es"). Auto-detected if not specified.
            format: Output format - "json", "text", or "srt"

        Returns:
            Dict with segments for JSON format, or string for text/srt.

        Raises:
            VideoNotFoundError: If the video is not found
            ServiceUnavailableError: If the service is unavailable
        """
        params = _build_get_params(lang, format)
        return self._client._request("GET", f"/v1/transcripts/{video_id}", params=params)

    def list_languages(self, video_id: str) -> dict[str, Any]:
        """
        List available transcript languages for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dict with video_id and languages list.
        """
        return self._client._request("GET", f"/v1/transcripts/{video_id}/languages")

    def get_text(self, video_id: str, lang: str | None = None) -> str:
        """Get transcript as plain text."""
        result = self.get(video_id, lang=lang, format="text")
        return result if isinstance(result, str) else result.get("text", "")

    def get_srt(self, video_id: str, lang: str | None = None) -> str:
        """Get transcript as SRT subtitles."""
        result = self.get(video_id, lang=lang, format="srt")
        return result if isinstance(result, str) else result.get("text", "")


class AsyncTranscriptsAPI:
    """Async transcripts API."""

    def __init__(self, client: Any):
        self._client = client

    async def get(
        self,
        video_id: str,
        lang: str | None = None,
        format: Literal["json", "text", "srt"] = "json",
    ) -> dict[str, Any] | str:
        """
        Get transcript for a YouTube video.

        Args:
            video_id: YouTube video ID (e.g., "dQw4w9WgXcQ")
            lang: Language code (e.g., "en", "es"). Auto-detected if not specified.
            format: Output format - "json", "text", or "srt"

        Returns:
            Dict with segments for JSON format, or string for text/srt.

        Raises:
            VideoNotFoundError: If the video is not found
            ServiceUnavailableError: If the service is unavailable
        """
        params = _build_get_params(lang, format)
        return await self._client._request("GET", f"/v1/transcripts/{video_id}", params=params)

    async def list_languages(self, video_id: str) -> dict[str, Any]:
        """List available transcript languages for a video."""
        return await self._client._request("GET", f"/v1/transcripts/{video_id}/languages")

    async def get_text(self, video_id: str, lang: str | None = None) -> str:
        """Get transcript as plain text."""
        result = await self.get(video_id, lang=lang, format="text")
        return result if isinstance(result, str) else result.get("text", "")

    async def get_srt(self, video_id: str, lang: str | None = None) -> str:
        """Get transcript as SRT subtitles."""
        result = await self.get(video_id, lang=lang, format="srt")
        return result if isinstance(result, str) else result.get("text", "")


def _build_get_params(
    lang: str | None, format: str
) -> dict[str, str] | None:
    params: dict[str, str] = {}
    if lang:
        params["lang"] = lang
    if format and format != "json":
        params["format"] = format
    return params or None
