from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row

from app.config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    indexed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_knowledge_created_at ON knowledge(created_at DESC);
"""


@contextmanager
def db() -> Iterator[psycopg.Connection]:
    with psycopg.connect(settings.postgres_url, row_factory=dict_row) as conn:
        conn.execute(SCHEMA)
        conn.commit()
        yield conn
