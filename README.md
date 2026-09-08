# Ask My Work

**Local-first AI work-memory agent.**

Ask My Work turns approved work context into a private, searchable knowledge base. It uses retrieval-augmented generation (RAG), not continuous LLM training.

## v0.1 goals

- Local FastAPI API and web UI
- Ollama for local chat and embeddings
- Qdrant vector database
- SQLite metadata store
- Notes and approved text events
- Secret redaction before indexing
- Read-only safety boundary: no shell execution, file modification, deletion, installation, or autonomous remediation

## Architecture

```text
Browser
   |
   v
FastAPI ---- SQLite (metadata)
   |
   +----> Redaction -> Chunking -> Embeddings -> Qdrant
   |                                      |
   +----> RAG context --------------------+
   |                                      |
   +------------------------------------> Ollama
                                          |
                                          v
                                        Answer
```

The future host agent will run outside Docker and collect only explicitly approved sources such as configured documents, screenshots, and notes.

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec ollama ollama pull qwen3:4b
docker compose exec ollama ollama pull nomic-embed-text
curl http://127.0.0.1:8000/health
```

Open `http://127.0.0.1:8000`.

## Test

```bash
docker compose run --rm api pytest -q
```

## Safety model

Phase 0/1 is deliberately read-only. The LLM cannot execute commands or directly modify the host. Any future action capability must go through an explicit policy engine and human approval.

See `docs/architecture.md` and `docs/security.md`.
