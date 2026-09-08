# Ask My Work

**Local-first AI work-memory agent.**

Ask My Work turns approved work context into a private, searchable knowledge base. It uses retrieval-augmented generation (RAG), not continuous LLM training.

## v0.1.1 stack

- FastAPI API and web UI
- **PostgreSQL** for application metadata and knowledge records
- **Qdrant** for vector search
- **Ollama running on the local host** for chat and embeddings
- Secret redaction before indexing
- Read-only safety boundary: no shell execution, file modification, deletion, installation, or autonomous remediation

There is **no SQLite database** and **no Ollama container**.

## Architecture

```text
Browser
   |
   v
FastAPI
   |
   +---- PostgreSQL (metadata / source records)
   |
   +---- Redaction -> Chunking -> Embeddings -> Qdrant
   |                                      |
   +---- RAG context --------------------+
   |                                      |
   +------------------------------------> Ollama (host)
                                          |
                                          v
                                        Answer
```

Docker Compose runs only the Ask My Work API, PostgreSQL, and Qdrant. Ollama is expected to already be running on the host at `11434`.

## Quick start

```bash
cp .env.example .env
# Set a strong POSTGRES_PASSWORD in .env
docker compose up -d --build
curl http://127.0.0.1:8000/health
```

Make sure Ollama is running on the host and the required models exist:

```bash
ollama list
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

Open `http://127.0.0.1:8000`.

## Services

| Service | Purpose | Port |
|---|---|---:|
| API | Application/API/UI | 8000 |
| PostgreSQL | Metadata and knowledge records | 5432 |
| Qdrant | Vector database | 6333 |
| Ollama | Local LLM + embeddings; host-managed | 11434 |

## Test

```bash
docker compose run --rm api pytest -q
```

## Safety model

Phase 0/1 is deliberately read-only. The LLM cannot execute commands or directly modify the host. Any future action capability must go through an explicit policy engine and human approval.

See `docs/architecture.md` and `docs/security.md`.
