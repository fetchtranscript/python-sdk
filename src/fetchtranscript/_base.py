"""Shared configuration for sync and async clients."""

from __future__ import annotations

__version__ = "0.1.3"

DEFAULT_BASE_URL = "https://api.fetchtranscript.com"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = f"FetchTranscript-Python/{__version__}"


def build_headers(api_key: str) -> dict[str, str]:
    """Build default headers for API requests."""
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
