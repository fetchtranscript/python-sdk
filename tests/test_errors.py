"""Tests for error mapping."""

import pytest
import httpx
import respx

from fetchtranscript import (
    FetchTranscriptClient,
    FetchTranscriptError,
    VideoNotFoundError,
    ChannelNotFoundError,
    InvalidVideoIdError,
    InsufficientCreditsError,
    AuthenticationError,
    ServiceUnavailableError,
)


@pytest.fixture
def client(mock_api, api_key, base_url):
    c = FetchTranscriptClient(api_key=api_key, base_url=base_url)
    yield c
    c.close()


class TestErrorMapping:
    def test_video_not_found(self, client, mock_api):
        mock_api.get("/v1/transcripts/bad_id").mock(
            return_value=httpx.Response(404, json={
                "error": "video_not_found",
                "message": "Video not found: bad_id",
            })
        )
        with pytest.raises(VideoNotFoundError) as exc_info:
            client.transcripts.get("bad_id")
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.message

    def test_invalid_api_key(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(401, json={
                "error": "invalid_api_key",
                "message": "Invalid API key",
            })
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.videos.get_metadata("dQw4w9WgXcQ")
        assert exc_info.value.status_code == 401

    def test_insufficient_credits(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(402, json={
                "error": "insufficient_credits",
                "message": "Not enough credits",
            })
        )
        with pytest.raises(InsufficientCreditsError):
            client.videos.get_metadata("dQw4w9WgXcQ")

    def test_service_unavailable(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(503, json={
                "error": "service_unavailable",
                "message": "Service temporarily unavailable",
            })
        )
        with pytest.raises(ServiceUnavailableError):
            client.videos.get_metadata("dQw4w9WgXcQ")

    def test_channel_not_found(self, client, mock_api):
        mock_api.get("/v1/channels/bad_channel").mock(
            return_value=httpx.Response(404, json={
                "error": "channel_not_found",
                "message": "Channel not found",
            })
        )
        with pytest.raises(ChannelNotFoundError):
            client.channels.get_info("bad_channel")

    def test_status_fallback_no_body(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(400, text="Bad Request")
        )
        with pytest.raises(InvalidVideoIdError):
            client.videos.get_metadata("dQw4w9WgXcQ")

    def test_exception_hierarchy(self):
        assert issubclass(VideoNotFoundError, FetchTranscriptError)
        assert issubclass(ChannelNotFoundError, FetchTranscriptError)
        assert issubclass(InvalidVideoIdError, FetchTranscriptError)
        assert issubclass(InsufficientCreditsError, FetchTranscriptError)
        assert issubclass(AuthenticationError, FetchTranscriptError)
        assert issubclass(ServiceUnavailableError, FetchTranscriptError)
