from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from pathlib import Path
import uuid, httpx
from app.config import settings
from app.db import db
from app.services.redaction import redact
from app.services.text import chunk_text

app=FastAPI(title=settings.app_name, version='0.1.0')
UI=Path('/app/ui/index.html')

class Note(BaseModel): title: str; content: str
class Chat(BaseModel): question: str
class Event(BaseModel): source: str='manual'; title: str=''; content: str

@app.get('/')
def home(): return FileResponse(UI)
@app.get('/health')
def health(): return {'status':'ok','app':settings.app_name,'mode':'read-only'}

async def embed(text):
    async with httpx.AsyncClient(timeout=120) as c:
        r=await c.post(f'{settings.ollama_url}/api/embed',json={'model':settings.embed_model,'input':text}); r.raise_for_status(); return r.json()['embeddings'][0]

@app.post('/api/v1/notes')
async def create_note(n: Note):
    content=redact(n.content); now=datetime.now(timezone.utc).isoformat(); nid=str(uuid.uuid4())
    with db() as conn: conn.execute('INSERT INTO knowledge VALUES (?,?,?,?,?)',(nid,n.title,content,'note',now)); conn.commit()
    # Indexing is best-effort until Qdrant dimension/model is discovered at startup.
    return {'id':nid,'title':n.title,'source':'note','created_at':now,'status':'stored'}

@app.post('/api/v1/events')
def create_event(e: Event):
    eid=str(uuid.uuid4()); now=datetime.now(timezone.utc).isoformat(); content=redact(e.content)
    with db() as conn: conn.execute('INSERT INTO knowledge VALUES (?,?,?,?,?)',(eid,e.title,content,e.source,now)); conn.commit()
    return {'id':eid,'status':'stored','read_only':True}

@app.post('/api/v1/search')
def search(q: Chat):
    with db() as conn: rows=conn.execute('SELECT id,title,content,source,created_at FROM knowledge WHERE content LIKE ? OR title LIKE ? ORDER BY created_at DESC LIMIT ?', (f'%{q.question}%',f'%{q.question}%',settings.top_k)).fetchall()
    return {'results':[dict(r) for r in rows]}

@app.post('/api/v1/chat')
async def chat(q: Chat):
    with db() as conn: rows=conn.execute('SELECT title,content,source,created_at FROM knowledge ORDER BY created_at DESC LIMIT ?', (settings.top_k,)).fetchall()
    context='\n\n'.join(f"[{r['source']}] {r['title']}: {r['content']}" for r in rows)
    prompt=f"You are Ask My Work, a local work-memory assistant. Answer only from the supplied work evidence. If evidence is insufficient, say so. Never invent commands or actions.\n\nEvidence:\n{context}\n\nQuestion: {q.question}"
    async with httpx.AsyncClient(timeout=180) as c:
        r=await c.post(f'{settings.ollama_url}/api/generate',json={'model':settings.chat_model,'prompt':prompt,'stream':False}); r.raise_for_status(); answer=r.json().get('response','')
    return {'answer':answer,'sources':[dict(r) for r in rows]}
