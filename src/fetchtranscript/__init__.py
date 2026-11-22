"""FetchTranscript - Official Python SDK for the FetchTranscript API."""

from ._base import __version__
from ._client import FetchTranscriptClient
from ._async_client import AsyncFetchTranscriptClient
from .errors import (
    AuthenticationError,
    ChannelNotFoundError,
    FetchTranscriptError,
    InsufficientCreditsError,
    InvalidVideoIdError,
    ServiceUnavailableError,
    VideoNotFoundError,
)

__all__ = [
    "__version__",
    "FetchTranscriptClient",
    "AsyncFetchTranscriptClient",
    "FetchTranscriptError",
    "VideoNotFoundError",
    "ChannelNotFoundError",
    "InvalidVideoIdError",
    "InsufficientCreditsError",
    "AuthenticationError",
    "ServiceUnavailableError",
]
