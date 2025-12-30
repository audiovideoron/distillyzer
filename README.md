# Distillyzer

Build a personal knowledge base from YouTube videos and GitHub repos. Transcribe, embed, and semantically search everything you care about.

## Why

YouTube's search is optimized for engagement, not learning. You watch a great 2-hour tutorial, forget where they explained that one thing, and spend 20 minutes scrubbing. GitHub repos have answers buried in code you'll never find with grep.

Distillyzer extracts knowledge from video and code, chunks it with timestamps, embeds it in a vector database, and lets you query it conversationally.

## How It Works

```
YouTube URL → yt-dlp → Whisper API → Chunks with timestamps → Embeddings → PostgreSQL/pgvector
GitHub URL  → git clone → Parse files → Chunks → Embeddings → PostgreSQL/pgvector
                                                                      ↓
                                              Your question → Embedding → Similarity search → Claude → Answer with sources
```

## Quick Start

```bash
# Install
git clone https://github.com/audiovideoron/distillyzer
cd distillyzer
uv venv && source .venv/bin/activate
uv pip install -e .

# Set up PostgreSQL with pgvector
createdb distillyzer
psql distillyzer < schema.sql

# Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and ANTHROPIC_API_KEY

# Harvest a video
dz harvest https://youtube.com/watch?v=...

# Query your knowledge
dz query "how does the auth system work?"

# Or chat interactively
dz chat
```

## Commands

| Command | Description |
|---------|-------------|
| `dz search "topic"` | Search YouTube without the clutter |
| `dz harvest <url>` | Download, transcribe, and embed a video or repo |
| `dz harvest-channel <url>` | List videos from a channel for selective harvesting |
| `dz query "question"` | Semantic search with Claude-generated answers |
| `dz chat` | Interactive conversation with your knowledge base |
| `dz stats` | Show what's in your knowledge base |

## Example

```bash
$ dz query "What are the core principles of agentic coding?"

╭─────────────────────── Answer ───────────────────────╮
│ Based on the sources, agentic coding centers on      │
│ "The Core Four": Context, Model, Prompt, and Tools.  │
│ The key shift is from writing code to orchestrating  │
│ systems that write code on your behalf...            │
╰──────────────────────────────────────────────────────╯

Sources:
  1. TAC: Hello Agentic Coding @ 13:17 (sim: 0.63)
  2. TAC: Hello Agentic Coding @ 20:05 (sim: 0.61)
```

## Tech Stack

- **yt-dlp** - YouTube download
- **OpenAI Whisper API** - Transcription with timestamps
- **OpenAI text-embedding-3-small** - 1536-dim embeddings
- **PostgreSQL + pgvector** - Vector similarity search
- **Claude API** - Answer generation
- **Typer + Rich** - CLI

## Requirements

- Python 3.12+
- PostgreSQL with pgvector extension
- yt-dlp (`brew install yt-dlp`)
- ffmpeg (`brew install ffmpeg`)
- OpenAI API key (for Whisper + embeddings)
- Anthropic API key (for Claude queries)

## Privacy

All data stays local. Videos are transcribed via API but the transcripts and embeddings live in your PostgreSQL database. Nothing is stored remotely or shared.

## License

MIT
