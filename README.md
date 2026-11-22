# FetchTranscript Python SDK

Official Python SDK for the [FetchTranscript](https://fetchtranscript.com) API — fetch YouTube transcripts, video metadata, channel info, and more.

## Installation

```bash
pip install fetchtranscript
```

## Quick Start

```python
from fetchtranscript import FetchTranscriptClient

client = FetchTranscriptClient(api_key="yt_your_api_key")

# Get a transcript
transcript = client.transcripts.get("dQw4w9WgXcQ")
for segment in transcript["segments"]:
    print(f"[{segment['start']:.1f}s] {segment['text']}")

# Get video metadata
video = client.videos.get_metadata("dQw4w9WgXcQ")
print(video["title"])
```

## Async Usage

```python
import asyncio
from fetchtranscript import AsyncFetchTranscriptClient

async def main():
    async with AsyncFetchTranscriptClient(api_key="yt_your_api_key") as client:
        transcript = await client.transcripts.get("dQw4w9WgXcQ")
        print(transcript["language"])

asyncio.run(main())
```

## API Reference

### Transcripts

```python
# Get transcript (JSON format with segments)
transcript = client.transcripts.get("VIDEO_ID")

# Get transcript in a specific language
transcript = client.transcripts.get("VIDEO_ID", lang="es")

# Get as plain text
text = client.transcripts.get_text("VIDEO_ID")

# Get as SRT subtitles
srt = client.transcripts.get_srt("VIDEO_ID")

# List available languages
languages = client.transcripts.list_languages("VIDEO_ID")
```

### Videos

```python
# Get video metadata
metadata = client.videos.get_metadata("VIDEO_ID")

# Get video chapters
chapters = client.videos.get_chapters("VIDEO_ID")

# Get video comments
comments = client.videos.get_comments("VIDEO_ID", limit=50)
```

### Channels

```python
# Get channel info
channel = client.channels.get_info("CHANNEL_ID")

# Get channel videos
videos = client.channels.get_videos("CHANNEL_ID", limit=20)

# Get all videos with auto-pagination
all_videos = client.channels.get_all_videos("CHANNEL_ID")
```

### Search

```python
# Search videos
results = client.search.videos("python tutorial", limit=10)

# Search and check transcript availability
results = client.search.find_videos_with_transcripts("python tutorial")
```

## Error Handling

The SDK raises domain-specific exceptions instead of raw HTTP errors:

```python
from fetchtranscript import (
    FetchTranscriptClient,
    VideoNotFoundError,
    InsufficientCreditsError,
    AuthenticationError,
)

client = FetchTranscriptClient(api_key="yt_your_api_key")

try:
    transcript = client.transcripts.get("invalid_id")
except VideoNotFoundError as e:
    print(f"Video not found: {e.message}")
except InsufficientCreditsError:
    print("Not enough credits")
except AuthenticationError:
    print("Invalid API key")
```

### Exception Hierarchy

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `FetchTranscriptError` | — | Base exception |
| `VideoNotFoundError` | 404 | Video not found or transcripts disabled |
| `ChannelNotFoundError` | 404 | Channel not found |
| `InvalidVideoIdError` | 400 | Invalid video/channel ID format |
| `InsufficientCreditsError` | 402 | Not enough credits |
| `AuthenticationError` | 401 | Missing or invalid API key |
| `ServiceUnavailableError` | 503 | Upstream service unavailable |

## Response Headers

After each request, you can check:

```python
client.transcripts.get("dQw4w9WgXcQ")
print(client.credits_remaining)    # Remaining API credits
print(client.processing_time_ms)   # Processing time in ms
```

## License

MIT
