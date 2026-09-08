# Architecture

## v0.1

```mermaid
flowchart TD
  B[Browser] --> A[FastAPI]
  A --> S[SQLite metadata]
  A --> R[Redaction]
  R --> E[Embedding / Indexing]
  E --> Q[Qdrant]
  A --> Q
  Q --> C[RAG context]
  C --> O[Ollama]
  O --> X[Answer]
```

### Boundaries
- The host is not exposed directly to the LLM.
- v0.1 has no shell execution or autonomous actions.
- Future collectors run as a separate host agent with explicit allowlisted paths.

## Evolution

```text
Observe -> Redact -> Understand -> Store -> Retrieve -> Document -> (future) Act with approval
```
