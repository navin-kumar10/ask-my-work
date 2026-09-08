import re

def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    words = text.split()
    if not words: return []
    chunks=[]; start=0
    while start < len(words):
        chunks.append(' '.join(words[start:start+size]))
        if start + size >= len(words): break
        start += max(1, size-overlap)
    return chunks

def slug(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')
