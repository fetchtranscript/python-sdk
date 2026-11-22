"""Tests for the synchronous FetchTranscript client."""

import pytest
import httpx
import respx

from fetchtranscript import FetchTranscriptClient, VideoNotFoundError, AuthenticationError


@pytest.fixture
def client(mock_api, api_key, base_url):
    c = FetchTranscriptClient(api_key=api_key, base_url=base_url)
    yield c
    c.close()


class TestClientInit:
    def test_creates_client(self, api_key):
        client = FetchTranscriptClient(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://api.fetchtranscript.com"
        client.close()

    def test_custom_base_url(self, api_key):
        client = FetchTranscriptClient(api_key=api_key, base_url="https://custom.api.com/")
        assert client.base_url == "https://custom.api.com"
        client.close()

    def test_context_manager(self, api_key):
        with FetchTranscriptClient(api_key=api_key) as client:
            assert client.api_key == api_key


class TestTranscripts:
    def test_get_transcript(self, client, mock_api):
        mock_api.get("/v1/transcripts/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "language": "en",
                "segments": [{"text": "Hello", "start": 0.0, "duration": 1.0}],
                "is_generated": False,
                "provider": "cache",
            })
        )
        result = client.transcripts.get("dQw4w9WgXcQ")
        assert result["video_id"] == "dQw4w9WgXcQ"
        assert len(result["segments"]) == 1

    def test_get_transcript_with_lang(self, client, mock_api):
        mock_api.get("/v1/transcripts/dQw4w9WgXcQ", params={"lang": "es"}).mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "language": "es",
                "segments": [],
                "is_generated": True,
                "provider": "cache",
            })
        )
        result = client.transcripts.get("dQw4w9WgXcQ", lang="es")
        assert result["language"] == "es"

    def test_list_languages(self, client, mock_api):
        mock_api.get("/v1/transcripts/dQw4w9WgXcQ/languages").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "languages": [
                    {"language_code": "en", "language": "English", "is_generated": False, "is_translatable": True},
                ],
            })
        )
        result = client.transcripts.list_languages("dQw4w9WgXcQ")
        assert len(result["languages"]) == 1


class TestVideos:
    def test_get_metadata(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "title": "Never Gonna Give You Up",
                "view_count": 1000000,
            })
        )
        result = client.videos.get_metadata("dQw4w9WgXcQ")
        assert result["title"] == "Never Gonna Give You Up"

    def test_get_chapters(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ/chapters").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "chapters": [],
                "has_chapters": False,
            })
        )
        result = client.videos.get_chapters("dQw4w9WgXcQ")
        assert result["has_chapters"] is False

    def test_get_comments(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ/comments").mock(
            return_value=httpx.Response(200, json={
                "video_id": "dQw4w9WgXcQ",
                "comments": [{"comment_id": "1", "text": "Great!", "author": "User"}],
                "total_count": 100,
                "has_more": True,
            })
        )
        result = client.videos.get_comments("dQw4w9WgXcQ")
        assert len(result["comments"]) == 1


class TestChannels:
    def test_get_info(self, client, mock_api):
        mock_api.get("/v1/channels/UCtest").mock(
            return_value=httpx.Response(200, json={
                "channel_id": "UCtest",
                "name": "Test Channel",
                "description": "A test channel",
            })
        )
        result = client.channels.get_info("UCtest")
        assert result["name"] == "Test Channel"

    def test_get_videos(self, client, mock_api):
        mock_api.get("/v1/channels/UCtest/videos").mock(
            return_value=httpx.Response(200, json={
                "channel_id": "UCtest",
                "videos": [{"video_id": "abc", "title": "Video 1"}],
                "total_count": 50,
                "has_more": True,
            })
        )
        result = client.channels.get_videos("UCtest")
        assert len(result["videos"]) == 1

    def test_get_videos_sends_defaults_matching_the_api(self, client, mock_api):
        """Regression: defaults (20, Shorts on) were never sent, so the API's applied."""
        route = mock_api.get("/v1/channels/UCtest/videos").mock(
            return_value=httpx.Response(200, json={"videos": [], "has_more": False})
        )
        client.channels.get_videos("UCtest")
        params = route.calls.last.request.url.params
        assert params["limit"] == "30"
        assert params["offset"] == "0"
        assert params["include_shorts"] == "false"

    def test_get_videos_include_shorts_is_sent(self, client, mock_api):
        """Regression: include_shorts=True never reached the API."""
        route = mock_api.get("/v1/channels/UCtest/videos").mock(
            return_value=httpx.Response(200, json={"videos": [], "has_more": False})
        )
        client.channels.get_videos("UCtest", limit=20, offset=40, include_shorts=True)
        params = route.calls.last.request.url.params
        assert params["limit"] == "20"
        assert params["offset"] == "40"
        assert params["include_shorts"] == "true"

    def test_get_all_videos_pages_of_100(self, client, mock_api):
        page = {"videos": [{"video_id": f"v{i}"} for i in range(100)], "has_more": True}
        last = {"videos": [{"video_id": "last"}], "has_more": False}
        route = mock_api.get("/v1/channels/UCtest/videos").mock(
            side_effect=[httpx.Response(200, json=page), httpx.Response(200, json=last)]
        )
        videos = client.channels.get_all_videos("UCtest", max_videos=500)
        assert len(videos) == 101
        assert [c.request.url.params["offset"] for c in route.calls] == ["0", "100"]
        assert route.calls[0].request.url.params["limit"] == "100"
        assert route.calls[0].request.url.params["include_shorts"] == "false"


class TestCommentsParams:
    def test_get_comments_sends_limit_and_sort(self, client, mock_api):
        route = mock_api.get("/v1/videos/dQw4w9WgXcQ/comments").mock(
            return_value=httpx.Response(200, json={"comments": [], "has_more": False})
        )
        client.videos.get_comments("dQw4w9WgXcQ", limit=250, sort="new")
        params = route.calls.last.request.url.params
        assert params["limit"] == "250"
        assert params["sort"] == "new"

    def test_get_comments_defaults(self, client, mock_api):
        route = mock_api.get("/v1/videos/dQw4w9WgXcQ/comments").mock(
            return_value=httpx.Response(200, json={"comments": [], "has_more": False})
        )
        client.videos.get_comments("dQw4w9WgXcQ")
        params = route.calls.last.request.url.params
        assert params["limit"] == "100"
        assert params["sort"] == "top"


class TestSearch:
    def test_search_videos(self, client, mock_api):
        mock_api.get("/v1/search").mock(
            return_value=httpx.Response(200, json={
                "query": "test",
                "results": [{"video_id": "abc", "title": "Test Video"}],
                "total_results": 1,
            })
        )
        result = client.search.videos("test")
        assert result["query"] == "test"
        assert len(result["results"]) == 1


class TestResponseHeaders:
    def test_credits_remaining(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(
                200,
                json={"video_id": "dQw4w9WgXcQ", "title": "Test"},
                headers={"x-credits-remaining": "42"},
            )
        )
        client.videos.get_metadata("dQw4w9WgXcQ")
        assert client.credits_remaining == 42

    def test_processing_time(self, client, mock_api):
        mock_api.get("/v1/videos/dQw4w9WgXcQ").mock(
            return_value=httpx.Response(
                200,
                json={"video_id": "dQw4w9WgXcQ", "title": "Test"},
                headers={"x-processing-time": "150"},
            )
        )
        client.videos.get_metadata("dQw4w9WgXcQ")
        assert client.processing_time_ms == 150

    def test_no_response_yet(self, api_key):
        client = FetchTranscriptClient(api_key=api_key)
        assert client.credits_remaining is None
        assert client.processing_time_ms is None
        client.close()
