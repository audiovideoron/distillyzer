# Distillyzer

Personal learning accelerator. Harvest knowledge from YouTube and GitHub, store it, query it, use it.

## What It Does

1. **Search** - Find YouTube content without the garbage UI
2. **Harvest** - Download videos, transcribe, clone repos
3. **Store** - Chunk and embed in PostgreSQL + pgvector
4. **Query** - Semantic search across everything you've collected
5. **Generate** - (Optional) Create outputs: posts, slides, docs

## Use Cases

- Research a topic (noise reduction, agentic engineering, WWII Eastern Front)
- Follow an expert (harvest their channel + repos)
- Query while building ("How did Dan implement auth?")
- Feed context to Claude for project work

## Tech Stack

| Layer | Tool |
|-------|------|
| YouTube search/download | yt-dlp |
| Transcription | OpenAI Whisper API |
| Embeddings | OpenAI text-embedding-3-small |
| Vector storage | PostgreSQL + pgvector |
| LLM queries | Claude API |
| GitHub | gitpython |
| CLI | Typer |
| Language | Python 3.12 |

## Project Structure

```
distillyzer/
├── src/distillyzer/
│   ├── cli.py        # Typer CLI commands
│   ├── harvest.py    # YouTube download + GitHub clone
│   ├── transcribe.py # Whisper API integration
│   ├── embed.py      # Chunking + embeddings
│   ├── query.py      # Semantic search + Claude
│   └── db.py         # PostgreSQL + pgvector
├── tests/
├── pyproject.toml
└── README.md
```

## CLI Design (Draft)

```bash
# Search YouTube
dz search "python async await" --limit 10

# Harvest a video
dz harvest https://youtube.com/watch?v=xxx

# Harvest a channel
dz harvest-channel @IndieDevDan --limit 50

# Harvest a GitHub repo
dz harvest-repo https://github.com/user/project

# Query your knowledge base
dz query "how does async/await work in Python?"

# Interactive chat mode
dz chat
```

## Database Schema (Draft)

```sql
-- Sources (channels, repos)
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- 'youtube_channel', 'github_repo'
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content items (videos, files)
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    type VARCHAR(20) NOT NULL, -- 'video', 'code_file'
    title VARCHAR(500),
    url TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks (searchable segments)
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id),
    content TEXT NOT NULL,
    chunk_index INTEGER,
    timestamp_start FLOAT, -- for video chunks
    timestamp_end FLOAT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for similarity search
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
```

## Environment Variables

```
DATABASE_URL=postgresql://user:pass@localhost/distillyzer
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Development

```bash
cd ~/distillyzer
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Status

Early design phase. Not yet functional.
