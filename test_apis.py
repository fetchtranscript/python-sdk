#!/usr/bin/env python3
"""
Integration test script for FetchTranscript API.

Run this to test all API endpoints against the live API.
Results are saved to the output/ directory as JSON files.

Usage:
    FETCHTRANSCRIPT_API_KEY=yt_xxx python test_apis.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from fetchtranscript import FetchTranscriptClient, FetchTranscriptError

# Configuration
API_KEY = os.getenv("FETCHTRANSCRIPT_API_KEY") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.fetchtranscript.com")

# Test video: Rick Astley - Never Gonna Give You Up
TEST_VIDEO_ID = "dQw4w9WgXcQ"
TEST_CHANNEL_ID = "UCuAXFkgsw1L7xaCfnd5JJOw"  # Rick Astley's channel

# Output directory
OUTPUT_DIR = Path(__file__).parent / "output"


def save_result(name: str, data: dict):
    """Save result to JSON file in output directory."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    filename = f"{name}.json"
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved: output/{filename}")


def test_endpoint(name: str, func, *args, **kwargs) -> dict:
    """Test an endpoint and return the result."""
    result = {
        "endpoint": name,
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "data": None,
        "error": None,
    }

    try:
        data = func(*args, **kwargs)
        result["success"] = True
        result["data"] = data
        print(f"  [OK] {name}")
    except FetchTranscriptError as e:
        result["error"] = {
            "type": type(e).__name__,
            "status_code": e.status_code,
            "message": e.message,
        }
        print(f"  [FAIL] {name} - {type(e).__name__}: {e.message}")
    except Exception as e:
        result["error"] = {
            "type": type(e).__name__,
            "message": str(e),
        }
        print(f"  [FAIL] {name} - {type(e).__name__}: {e}")

    return result


def main():
    """Run all tests."""
    print("\n" + "#" * 60)
    print("#  FetchTranscript API Test Suite")
    print("#" * 60)

    if not API_KEY:
        print("\nERROR: API key not found in environment!")
        print("Set FETCHTRANSCRIPT_API_KEY=yt_xxx")
        sys.exit(1)

    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...")
    print(f"Test Video: {TEST_VIDEO_ID}")
    print(f"Test Channel: {TEST_CHANNEL_ID}")
    print(f"\nResults will be saved to: {OUTPUT_DIR}/")

    client = FetchTranscriptClient(
        api_key=API_KEY,
        base_url=API_BASE_URL,
    )

    results = {}

    try:
        # Health Check
        print("\n" + "=" * 40)
        print("Health Check")
        print("=" * 40)
        results["health"] = test_endpoint("health", client.health_check)
        save_result("01_health", results["health"])

        # Transcripts API
        print("\n" + "=" * 40)
        print("Transcripts API")
        print("=" * 40)

        results["transcript_json"] = test_endpoint(
            "transcript_json",
            client.transcripts.get,
            TEST_VIDEO_ID,
            format="json"
        )
        save_result("02_transcript_json", results["transcript_json"])

        results["transcript_text"] = test_endpoint(
            "transcript_text",
            client.transcripts.get,
            TEST_VIDEO_ID,
            format="text"
        )
        save_result("03_transcript_text", results["transcript_text"])

        results["transcript_srt"] = test_endpoint(
            "transcript_srt",
            client.transcripts.get,
            TEST_VIDEO_ID,
            format="srt"
        )
        save_result("04_transcript_srt", results["transcript_srt"])

        results["languages"] = test_endpoint(
            "languages",
            client.transcripts.list_languages,
            TEST_VIDEO_ID
        )
        save_result("05_languages", results["languages"])

        # Videos API
        print("\n" + "=" * 40)
        print("Videos API")
        print("=" * 40)

        results["video_metadata"] = test_endpoint(
            "video_metadata",
            client.videos.get_metadata,
            TEST_VIDEO_ID
        )
        save_result("06_video_metadata", results["video_metadata"])

        results["video_chapters"] = test_endpoint(
            "video_chapters",
            client.videos.get_chapters,
            TEST_VIDEO_ID
        )
        save_result("07_video_chapters", results["video_chapters"])

        results["video_comments"] = test_endpoint(
            "video_comments",
            client.videos.get_comments,
            TEST_VIDEO_ID,
            limit=10
        )
        save_result("08_video_comments", results["video_comments"])

        # Channels API
        print("\n" + "=" * 40)
        print("Channels API")
        print("=" * 40)

        results["channel_info"] = test_endpoint(
            "channel_info",
            client.channels.get_info,
            TEST_CHANNEL_ID
        )
        save_result("09_channel_info", results["channel_info"])

        results["channel_videos"] = test_endpoint(
            "channel_videos",
            client.channels.get_videos,
            TEST_CHANNEL_ID,
            limit=5
        )
        save_result("10_channel_videos", results["channel_videos"])

        # Search API
        print("\n" + "=" * 40)
        print("Search API")
        print("=" * 40)

        results["search"] = test_endpoint(
            "search",
            client.search.videos,
            "rick astley never gonna give you up",
            limit=5
        )
        save_result("11_search", results["search"])

        # Summary
        print("\n" + "=" * 40)
        print("Summary")
        print("=" * 40)

        success_count = sum(1 for r in results.values() if r.get("success"))
        total_count = len(results)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "api_base_url": API_BASE_URL,
            "test_video_id": TEST_VIDEO_ID,
            "test_channel_id": TEST_CHANNEL_ID,
            "credits_remaining": client.credits_remaining,
            "total_tests": total_count,
            "passed": success_count,
            "failed": total_count - success_count,
            "results": {
                name: {
                    "success": r.get("success"),
                    "error": r.get("error", {}).get("type") if r.get("error") else None
                }
                for name, r in results.items()
            }
        }

        save_result("00_summary", summary)

        print(f"\n  Tests: {success_count}/{total_count} passed")
        print(f"  Credits remaining: {client.credits_remaining}")
        print(f"\n  All results saved to: {OUTPUT_DIR}/")

    finally:
        client.close()


if __name__ == "__main__":
    main()
