from datetime import datetime, timezone
from pathlib import Path
import uuid

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.db import db
from app.services.redaction import redact

app = FastAPI(title=settings.app_name, version="0.1.1")
UI = Path("/app/ui/index.html")


class Note(BaseModel):
    title: str
    content: str


class Chat(BaseModel):
    question: str


class Event(BaseModel):
    source: str = "manual"
    title: str = ""
    content: str


@app.get("/")
def home():
    return FileResponse(UI)


@app.get("/health")
def health():
    with db() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "app": settings.app_name, "mode": "read-only"}


async def ollama_generate(prompt: str):
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(
            f"{settings.ollama_url}/api/generate",
            json={"model": settings.chat_model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json().get("response", "")


@app.post("/api/v1/notes")
def create_note(note: Note):
    content = redact(note.content)
    now = datetime.now(timezone.utc)
    note_id = str(uuid.uuid4())
    with db() as conn:
        conn.execute(
            "INSERT INTO knowledge (id, title, content, source, created_at) VALUES (%s, %s, %s, %s, %s)",
            (note_id, note.title, content, "note", now),
        )
        conn.commit()
    return {"id": note_id, "title": note.title, "source": "note", "created_at": now.isoformat(), "status": "stored"}


@app.post("/api/v1/events")
def create_event(event: Event):
    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    content = redact(event.content)
    with db() as conn:
        conn.execute(
            "INSERT INTO knowledge (id, title, content, source, created_at) VALUES (%s, %s, %s, %s, %s)",
            (event_id, event.title, content, event.source, now),
        )
        conn.commit()
    return {"id": event_id, "status": "stored", "read_only": True}


@app.post("/api/v1/search")
def search(query: Chat):
    pattern = f"%{query.question}%"
    with db() as conn:
        rows = conn.execute(
            "SELECT id, title, content, source, created_at FROM knowledge "
            "WHERE content ILIKE %s OR title ILIKE %s ORDER BY created_at DESC LIMIT %s",
            (pattern, pattern, settings.top_k),
        ).fetchall()
    return {"results": rows}


@app.post("/api/v1/chat")
async def chat(query: Chat):
    with db() as conn:
        rows = conn.execute(
            "SELECT id, title, content, source, created_at FROM knowledge "
            "ORDER BY created_at DESC LIMIT %s",
            (settings.top_k,),
        ).fetchall()

    context = "\n\n".join(
        f"[{row['source']}] {row['title']}: {row['content']}" for row in rows
    )
    prompt = (
        "You are Ask My Work, a local work-memory assistant. "
        "Answer only from the supplied work evidence. If evidence is insufficient, say so. "
        "Never invent commands or actions.\n\n"
        f"Evidence:\n{context}\n\nQuestion: {query.question}"
    )
    answer = await ollama_generate(prompt)
    return {"answer": answer, "sources": rows}
