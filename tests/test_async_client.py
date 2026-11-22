"""Tests for the asynchronous FetchTranscript client."""

import pytest
import pytest_asyncio
import httpx
import respx

from fetchtranscript import AsyncFetchTranscriptClient, VideoNotFoundError


@pytest_asyncio.fixture
async def client(base_url, api_key):
    c = AsyncFetchTranscriptClient(api_key=api_key, base_url=base_url)
    yield c
    await c.close()


@pytest.mark.asyncio
class TestAsyncTranscripts:
    async def test_get_transcript(self, client, mock_api):
        mock_api.get("/v1/transcripts/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "language": "en",
                "segments": [{"text": "Hello", "start": 0.0, "duration": 1.0}],
                "is_generated": False,
                "provider": "cache",
            })
        )
        result = await client.transcripts.get("dQw4w9WgXcQ")
        assert result["video_id"] == "dQw4w9WgXcQ"

    async def test_list_languages(self, client, mock_api):
        mock_api.get("/v1/transcripts/dQw4w9WgXcQ/languages").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "languages": [
                    {"language_code": "en", "language": "English", "is_generated": False, "is_translatable": True},
                ],
            })
        )
        result = await client.transcripts.list_languages("dQw4w9WgXcQ")
        assert len(result["languages"]) == 1


@pytest.mark.asyncio
class TestAsyncVideos:
    async def test_get_metadata(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "title": "Never Gonna Give You Up",
            })
        )
        result = await client.videos.get_metadata("dQw4w9WgXcQ")
        assert result["title"] == "Never Gonna Give You Up"


@pytest.mark.asyncio
class TestAsyncContextManager:
    async def test_async_with(self, mock_api, api_key, base_url):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(200, json={"video_id": "dQw4w9WgXcQ", "title": "Test"})
        )
        async with AsyncFetchTranscriptClient(api_key=api_key, base_url=base_url) as client:
            result = await client.videos.get_metadata("dQw4w9WgXcQ")
            assert result["title"] == "Test"
