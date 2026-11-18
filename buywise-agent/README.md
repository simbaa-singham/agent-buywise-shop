# buywise-agent

The AI agent (Python, LangGraph): routes each message, calls tools through MCP, answers from documents with RAG, streams replies through Redis. Also runs the document ingestion worker.

**Open in:** PyCharm -> open `buywise-agent/` (interpreter: `buywise-agent/.venv`, created by uv). Attach `buywise-mcp/` to the same window (File > Open > Attach) with its own `.venv`.

## Contents
| Path | Purpose |
|---|---|
| `buywise_agent/api.py` | FastAPI app: `POST /turns` (202, the turn runs in the background, ADR-029) |
| `buywise_agent/graph.py` | LangGraph agent loop (LLM -> tools -> LLM), quote-then-yes ordering |
| `buywise_agent/tools.py` | The tools the LLM can call: MCP tools on buywise-mcp plus knowledge search |
| `buywise_agent/events.py` | Writes chat contract events to the Redis Stream `conv:{id}` |
| `buywise_agent/rag/` | Ingest (parse, chunk, embed into `rag.chunks`) and vector search; the table itself is created by `buywise-db/agent/` (ADR-046) |
| `buywise_agent/config.py` | Settings (env vars or `.env`; defaults match the local stack) |
| `buywise_agent/contracts/` | Generated chat contract models (Pydantic) |
| `tests/contract/` | Contract tests; `tests/turn.py` runs one chat turn from the terminal |
| `pyproject.toml, uv.lock, .python-version` | Dependencies, exact pinned versions, Python version (uv, ADR-042) |
| `.env.example` | Local settings |
| `Makefile` | dev, lock, test, lint, ingest, run, turn |
| `../buywise-docs/03-buywise-agent/` | 01-design.md, 02-rag.md, 03-learning.md (docs live in buywise-docs, ADR-048) |

## Run
Needs uv (`brew install uv`). `make agent-dev` (create .venv from uv.lock), `make test` (tests + lint), `make ingest` (knowledge docs from `../buywise-data/knowledge` into pgvector; needs Ollama), `make -C buywise-agent run` -> http://localhost:8000, `make -C buywise-agent turn Q="..."` (one turn in the terminal). After editing dependencies in pyproject.toml: `make -C buywise-agent lock`.

## Documents
- [buywise-docs/03-buywise-agent/01-design.md](../buywise-docs/03-buywise-agent/01-design.md) - detailed design
- [buywise-docs/03-buywise-agent/02-rag.md](../buywise-docs/03-buywise-agent/02-rag.md) - RAG design
- [buywise-docs/03-buywise-agent/03-learning.md](../buywise-docs/03-buywise-agent/03-learning.md) - learning notes per phase
- System overview: [buywise-docs/00-architecture-overview.md](../buywise-docs/00-architecture-overview.md); roadmap: [buywise-docs/09-implementation-roadmap.md](../buywise-docs/09-implementation-roadmap.md)

## Decisions that apply (central log: buywise-docs/10-adr/01-adr-log.md)
| ADR | Decision |
|---|---|
| [ADR-008](../buywise-docs/10-adr/01-adr-log.md) | LangGraph 1.2 for agent orchestration with Postgres checkpointer |
| [ADR-011](../buywise-docs/10-adr/01-adr-log.md) | Postgres + pgvector + full-text for RAG (hybrid, RRF, rerank); retriever interface; `pg_search` BM25 upgrade path; RAG reads off the primary in pro... |
| [ADR-026](../buywise-docs/10-adr/01-adr-log.md) | LLM metering and budgets: LiteLLM model gateway (pricing, spend, global budget, rate limits) + agent LLM client (per-turn/conversation/customer cap... |
| [ADR-027](../buywise-docs/10-adr/01-adr-log.md) | LLM observability in the UI: Grafana for trends/alerts + staff-console AI Operations (ops-admin) + customer-web dev overlay; `status.updated` and `... |
| [ADR-028](../buywise-docs/10-adr/01-adr-log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop Node server -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-029](../buywise-docs/10-adr/01-adr-log.md) | Agent output path: background turns (`POST /turns` 202); agent appends ADR-024 events to per-conversation Redis Stream; Node server pods read and forward; ... |
| [ADR-030](../buywise-docs/10-adr/01-adr-log.md) | Intent routing: cascade of rules -> fast in-process classifier -> economy-tier LLM classifier; clarify then handoff on low confidence; flow stickin... |
| [ADR-034](../buywise-docs/10-adr/01-adr-log.md) | RAG chunking: structure-aware per doc type, parent-child retrieval, context headers, metadata filters; sizes tuned with Ragas; applied to the ADR-0... |
| [ADR-036](../buywise-docs/10-adr/01-adr-log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-039](../buywise-docs/10-adr/01-adr-log.md) | Multi-format ingestion: detect by magic bytes -> parser plugin per format -> common Document model with provenance -> normalize, validate, clean, c... |
| [ADR-040](../buywise-docs/10-adr/01-adr-log.md) | Embeddings: bge-m3 in every environment via LiteLLM; `model_version` per vector; PII-masked queries; phase-3 bake-off; model change via blue/green ... |
| [ADR-042](../buywise-docs/10-adr/01-adr-log.md) | uv for every Python project: `pyproject.toml` + committed `uv.lock` + `.python-version`; `uv sync --locked` locally and in CI |
