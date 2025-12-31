"""initial schema

Revision ID: bff6dc76c2f7
Revises: 
Create Date: 2025-12-31 07:11:53.344854

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bff6dc76c2f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Sources (channels, repos)
    op.execute("""
        CREATE TABLE sources (
            id SERIAL PRIMARY KEY,
            type VARCHAR(20) NOT NULL,
            name VARCHAR(255) NOT NULL,
            url TEXT NOT NULL UNIQUE,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Content items (videos, files)
    op.execute("""
        CREATE TABLE items (
            id SERIAL PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id),
            type VARCHAR(20) NOT NULL,
            title VARCHAR(500),
            url TEXT UNIQUE,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Chunks (searchable segments with embeddings)
    op.execute("""
        CREATE TABLE chunks (
            id SERIAL PRIMARY KEY,
            item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            chunk_index INTEGER,
            timestamp_start FLOAT,
            timestamp_end FLOAT,
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # Vector similarity index
    op.execute("""
        CREATE INDEX chunks_embedding_idx ON chunks
        USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10)
    """)

    # Skills table
    op.execute("""
        CREATE TABLE skills (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            type VARCHAR(50) NOT NULL,
            description TEXT,
            content TEXT NOT NULL,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS skills CASCADE")
    op.execute("DROP TABLE IF EXISTS chunks CASCADE")
    op.execute("DROP TABLE IF EXISTS items CASCADE")
    op.execute("DROP TABLE IF EXISTS sources CASCADE")
    op.execute("DROP EXTENSION IF EXISTS vector")
