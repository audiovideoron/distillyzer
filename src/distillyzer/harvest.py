"""Harvest content from YouTube and articles."""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import trafilatura

from . import db


class HarvestError(Exception):
    """Base exception for harvest operations."""
    pass


class YtDlpError(HarvestError):
    """Exception raised when yt-dlp command fails."""
    pass


def parse_youtube_url(url: str) -> dict:
    """Parse YouTube URL to extract video ID and type."""
    # Video patterns
    video_patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in video_patterns:
        match = re.search(pattern, url)
        if match:
            return {"type": "video", "id": match.group(1)}

    # Channel patterns
    channel_patterns = [
        r"youtube\.com/@([a-zA-Z0-9_-]+)",
        r"youtube\.com/channel/([a-zA-Z0-9_-]+)",
        r"youtube\.com/c/([a-zA-Z0-9_-]+)",
    ]
    for pattern in channel_patterns:
        match = re.search(pattern, url)
        if match:
            return {"type": "channel", "id": match.group(1)}

    return {"type": "unknown", "id": None}


def get_video_info(url: str) -> dict:
    """Get video metadata using yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-download", url],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except FileNotFoundError:
        raise YtDlpError("yt-dlp is not installed or not found in PATH")
    except subprocess.CalledProcessError as e:
        raise YtDlpError(f"yt-dlp failed to get video info: {e.stderr}")
    except json.JSONDecodeError as e:
        raise YtDlpError(f"Failed to parse yt-dlp output: {e}")


def download_audio(url: str, output_dir: Path) -> Path:
    """Download audio from YouTube video using yt-dlp. Uses 64k bitrate to stay under Whisper's 25MB limit."""
    output_template = str(output_dir / "%(id)s.%(ext)s")
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "-x",  # Extract audio
                "--audio-format", "mp3",
                "--audio-quality", "9",  # Lower quality = smaller file (64kbps)
                "--postprocessor-args", "ffmpeg:-ac 1 -ar 16000",  # Mono, 16kHz (fine for speech)
                "-o", output_template,
                url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise YtDlpError("yt-dlp is not installed or not found in PATH")
    except subprocess.CalledProcessError as e:
        raise YtDlpError(f"yt-dlp failed to download audio: {e.stderr}")

    # Find the downloaded file
    for f in output_dir.iterdir():
        if f.suffix == ".mp3":
            return f
    raise YtDlpError("Audio file not found after download")


def search_youtube(query: str, limit: int = 10) -> list[dict]:
    """Search YouTube using yt-dlp."""
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--no-download",
                f"ytsearch{limit}:{query}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise YtDlpError("yt-dlp is not installed or not found in PATH")
    except subprocess.CalledProcessError as e:
        raise YtDlpError(f"yt-dlp search failed: {e.stderr}")

    videos = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                data = json.loads(line)
                videos.append({
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "url": f"https://youtube.com/watch?v={data.get('id')}",
                    "channel": data.get("channel"),
                    "duration": data.get("duration"),
                })
            except json.JSONDecodeError:
                # Skip malformed lines
                continue
    return videos


def harvest_video(url: str) -> dict:
    """
    Harvest a YouTube video: download audio, get metadata, save to DB.
    Returns dict with item_id and audio_path.
    """
    # Check if already harvested
    existing = db.get_item_by_url(url)
    if existing:
        return {"item_id": existing["id"], "status": "already_exists", "title": existing["title"]}

    # Get video info
    info = get_video_info(url)
    title = info.get("title", "Unknown")
    channel = info.get("channel", "Unknown")
    duration = info.get("duration", 0)

    # Download audio to temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix="distillyzer_"))
    audio_path = download_audio(url, temp_dir)

    # Get or create source for channel
    channel_url = info.get("channel_url", f"https://youtube.com/@{channel}")
    source_id = db.get_or_create_source(
        type="youtube_channel",
        name=channel,
        url=channel_url,
    )

    # Create item in DB
    item_id = db.create_item(
        source_id=source_id,
        type="video",
        title=title,
        url=url,
        metadata={
            "channel": channel,
            "duration": duration,
            "video_id": info.get("id"),
        },
    )

    return {
        "item_id": item_id,
        "audio_path": str(audio_path),
        "title": title,
        "channel": channel,
        "duration": duration,
        "status": "downloaded",
    }


def harvest_channel(channel_url: str, limit: int = 50) -> list[dict]:
    """Harvest videos from a YouTube channel."""
    # Get channel videos
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--no-download",
                "--playlist-end", str(limit),
                channel_url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise YtDlpError("yt-dlp is not installed or not found in PATH")
    except subprocess.CalledProcessError as e:
        raise YtDlpError(f"yt-dlp failed to harvest channel: {e.stderr}")

    videos = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                data = json.loads(line)
                video_url = f"https://youtube.com/watch?v={data.get('id')}"
                videos.append({
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "url": video_url,
                })
            except json.JSONDecodeError:
                # Skip malformed lines
                continue
    return videos


# --- Articles ---

def harvest_article(url: str) -> dict:
    """
    Harvest an article from a URL.
    Extracts main content, creates item in DB.
    Returns dict with item_id and content for embedding.
    """
    # Check if already harvested
    existing = db.get_item_by_url(url)
    if existing:
        return {"item_id": existing["id"], "status": "already_exists", "title": existing["title"]}

    # Fetch and extract article content
    # Use custom headers to avoid blocks from sites like Medium
    import requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        downloaded = response.text
    except Exception as e:
        raise RuntimeError(f"Failed to fetch URL: {url} - {e}")

    # Extract main content as plain text
    content = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=True,
    )

    if not content or len(content) < 100:
        raise RuntimeError(f"Could not extract meaningful content from: {url}")

    # Extract metadata
    metadata = trafilatura.extract_metadata(downloaded)
    title = metadata.title if metadata and metadata.title else _title_from_url(url)
    author = metadata.author if metadata and metadata.author else None
    sitename = (metadata.sitename if metadata and metadata.sitename else None) or urlparse(url).netloc

    # Get or create source for the site
    source_id = db.get_or_create_source(
        type="website",
        name=sitename,
        url=f"https://{urlparse(url).netloc}",
    )

    # Create item in DB
    item_id = db.create_item(
        source_id=source_id,
        type="article",
        title=title,
        url=url,
        metadata={
            "author": author,
            "sitename": sitename,
            "content_length": len(content),
        },
    )

    return {
        "item_id": item_id,
        "title": title,
        "author": author,
        "sitename": sitename,
        "content": content,
        "status": "harvested",
    }


def _title_from_url(url: str) -> str:
    """Generate a title from URL path."""
    path = urlparse(url).path
    # Get last path segment, clean it up
    segments = [s for s in path.split("/") if s]
    if segments:
        title = segments[-1].replace("-", " ").replace("_", " ")
        return title[:100]
    return "Untitled Article"
