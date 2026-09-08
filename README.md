# Ask My Work

Local-first AI work-memory assistant.

## V0.1 architecture

```text
FastAPI
  ↓
Notes / Events
  ↓
Secret Redaction
  ↓
PostgreSQL
  ↓
RAG
  ↓
Qdrant
  ↓
Ollama
  ↓
Ask My Work UI
```

### Data responsibilities

- **PostgreSQL** — durable application metadata and redacted knowledge records.
- **Qdrant** — semantic vector index used by RAG retrieval.
- **Ollama** — local chat and embedding models, already running on the host.
- **FastAPI** — ingestion, retrieval, RAG orchestration, and UI API.

There is no SQLite database and no Ollama container.

## Repository structure

```text
ask-my-work/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   └── services/
│       ├── redaction.py
│       ├── text.py
│       └── qdrant_store.py
│
├── ui/
│   └── index.html
│
├── docs/
│   ├── architecture.md
│   └── security.md
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Runtime

Docker Compose runs only:

```text
ask-my-work-api       :8000
ask-my-work-postgres  :5432
ask-my-work-qdrant    :6333
```

Ollama is host-managed:

```text
http://127.0.0.1:11434
```

From the API container it is reached through `host.docker.internal`.

## Quick start

```bash
cp .env.example .env
# Set POSTGRES_PASSWORD in .env
docker compose up -d --build

ollama list
ollama pull qwen3:4b
ollama pull nomic-embed-text

curl http://127.0.0.1:8000/health
```

Open `http://127.0.0.1:8000`.

## Test

```bash
docker compose run --rm api pytest -q
```

## Safety

V0.1 is read-only. The model cannot execute shell commands, modify host files, install software, delete data, or autonomously remediate infrastructure.

See `docs/architecture.md` and `docs/security.md`.
