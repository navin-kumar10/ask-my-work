import sqlite3
from contextlib import contextmanager
from app.config import settings

@contextmanager
def db():
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS knowledge (id TEXT PRIMARY KEY, title TEXT, content TEXT, source TEXT, created_at TEXT)''')
        conn.commit()
        yield conn
    finally:
        conn.close()
