from datetime import datetime, timezone
from pathlib import Path
import uuid

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.db import db
from app.services.qdrant_store import QdrantStore
from app.services.redaction import redact
from app.services.text import chunk_text

app = FastAPI(title=settings.app_name, version="0.1.0")
UI = Path("/app/ui/index.html")
store = QdrantStore()


class Note(BaseModel):
    title: str
    content: str


class Chat(BaseModel):
    question: str


class Event(BaseModel):
    source: str = "manual"
    title: str = ""
    content: str


async def ollama_json(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(f"{settings.ollama_url}{path}", json=payload)
        response.raise_for_status()
        return response.json()


async def embed(text: str) -> list[float]:
    data = await ollama_json("/api/embed", {"model": settings.embed_model, "input": text})
    return data["embeddings"][0]


@app.get("/")
def home():
    return FileResponse(UI)


@app.get("/health")
def health():
    with db() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "app": settings.app_name, "mode": "read-only"}


async def index_document(document_id: str, title: str, content: str, source: str):
    chunks = chunk_text(content)
    points = []
    for index, chunk in enumerate(chunks):
        vector = await embed(chunk)
        points.append({
            "id": f"{document_id}:{index}",
            "vector": vector,
            "payload": {"knowledge_id": document_id, "title": title, "content": chunk, "source": source},
        })
    if points:
        store.ensure(len(points[0]["vector"]))
        store.upsert(points)
    with db() as conn:
        conn.execute("UPDATE knowledge SET indexed_at=%s WHERE id=%s", (datetime.now(timezone.utc), document_id))
        conn.commit()


async def save_knowledge(title: str, content: str, source: str) -> str:
    knowledge_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    with db() as conn:
        conn.execute(
            "INSERT INTO knowledge (id, title, content, source, created_at) VALUES (%s, %s, %s, %s, %s)",
            (knowledge_id, title, content, source, now),
        )
        conn.commit()
    await index_document(knowledge_id, title, content, source)
    return knowledge_id


@app.post("/api/v1/notes")
async def create_note(note: Note):
    content = redact(note.content)
    note_id = await save_knowledge(note.title, content, "note")
    return {"id": note_id, "title": note.title, "source": "note", "status": "indexed"}


@app.post("/api/v1/events")
async def create_event(event: Event):
    content = redact(event.content)
    event_id = await save_knowledge(event.title, content, event.source)
    return {"id": event_id, "status": "indexed", "read_only": True}


@app.post("/api/v1/search")
async def search(query: Chat):
    vector = await embed(query.question)
    points = store.search(vector, settings.top_k)
    return {"results": [point.payload | {"score": point.score} for point in points]}


@app.post("/api/v1/chat")
async def chat(query: Chat):
    vector = await embed(query.question)
    points = store.search(vector, settings.top_k)
    context = "\n\n".join(
        f"[{p.payload.get('source')}] {p.payload.get('title')}: {p.payload.get('content')}"
        for p in points
    )
    prompt = (
        "You are Ask My Work, a local work-memory assistant. Answer only from the supplied evidence. "
        "If evidence is insufficient, say so. Never invent facts, commands, or actions.\n\n"
        f"Evidence:\n{context}\n\nQuestion: {query.question}"
    )
    data = await ollama_json("/api/generate", {"model": settings.chat_model, "prompt": prompt, "stream": False})
    sources = [p.payload | {"score": p.score} for p in points]
    return {"answer": data.get("response", ""), "sources": sources}
