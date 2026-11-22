"""Domain-specific exceptions for the FetchTranscript SDK."""

from __future__ import annotations

import httpx


class FetchTranscriptError(Exception):
    """Base error for FetchTranscript API."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class VideoNotFoundError(FetchTranscriptError):
    """Video was not found or is unavailable."""


class ChannelNotFoundError(FetchTranscriptError):
    """Channel was not found."""


class InvalidVideoIdError(FetchTranscriptError):
    """Invalid video ID format."""


class InsufficientCreditsError(FetchTranscriptError):
    """Not enough credits to make the request."""


class AuthenticationError(FetchTranscriptError):
    """Missing or invalid API key."""


class ServiceUnavailableError(FetchTranscriptError):
    """Upstream service is unavailable."""


# Map API error codes to exception classes
_ERROR_MAP: dict[str, type[FetchTranscriptError]] = {
    "video_not_found": VideoNotFoundError,
    "transcripts_disabled": VideoNotFoundError,
    "no_transcript_found": VideoNotFoundError,
    "channel_not_found": ChannelNotFoundError,
    "invalid_video_id": InvalidVideoIdError,
    "invalid_channel_id": InvalidVideoIdError,
    "insufficient_credits": InsufficientCreditsError,
    "missing_api_key": AuthenticationError,
    "invalid_api_key": AuthenticationError,
    "service_unavailable": ServiceUnavailableError,
}

_STATUS_MAP: dict[int, type[FetchTranscriptError]] = {
    400: InvalidVideoIdError,
    401: AuthenticationError,
    402: InsufficientCreditsError,
    404: VideoNotFoundError,
    503: ServiceUnavailableError,
}


def raise_for_status(response: httpx.Response) -> None:
    """Raise a domain-specific exception if the response indicates an error."""
    if response.is_success:
        return

    message = f"HTTP {response.status_code}"
    error_code = None
    try:
        body = response.json()
        if isinstance(body, dict):
            error_code = body.get("error")
            message = body.get("message", message)
            if "detail" in body and isinstance(body["detail"], dict):
                error_code = body["detail"].get("error", error_code)
                message = body["detail"].get("message", message)
    except Exception:
        message = response.text or message

    exc_class = FetchTranscriptError
    if error_code and error_code in _ERROR_MAP:
        exc_class = _ERROR_MAP[error_code]
    elif response.status_code in _STATUS_MAP:
        exc_class = _STATUS_MAP[response.status_code]

    raise exc_class(message, status_code=response.status_code)
