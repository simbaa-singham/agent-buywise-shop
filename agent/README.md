# agent - buywise-agent

The AI agent (Python, LangGraph): routes each message, calls tools through MCP, answers from documents with RAG, streams replies through Redis. Also runs the document ingestion worker.

**Open in:** PyCharm -> open `agent/` (interpreter: `agent/.venv`). Attach `mcp/` to the same window (File > Open > Attach) with its own `.venv`.

## Contents
| Path | Purpose |
|---|---|
| `buywise_agent/contracts/` | Generated chat contract models (Pydantic) |
| `tests/contract/` | Contract tests |
| `pyproject.toml, .env.example` | Dependencies and local settings |
| `Makefile` | dev, test, lint, ingest |
| `docs/` | design.md, rag.md, learning.md |

## Run
`make agent-dev` (create .venv), `make test` (tests + lint).

## Documents
- [docs/design.md](docs/design.md) - detailed design
- [docs/rag.md](docs/rag.md) - RAG design
- [docs/learning.md](docs/learning.md) - learning notes per phase
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-008](../docs/adr/ADR_Log.md) | LangGraph 1.2 for agent orchestration with Postgres checkpointer |
| [ADR-011](../docs/adr/ADR_Log.md) | Postgres + pgvector + full-text for RAG (hybrid, RRF, rerank); retriever interface; `pg_search` BM25 upgrade path; RAG reads off the primary in pro... |
| [ADR-026](../docs/adr/ADR_Log.md) | LLM metering and budgets: LiteLLM model gateway (pricing, spend, global budget, rate limits) + agent LLM client (per-turn/conversation/customer cap... |
| [ADR-027](../docs/adr/ADR_Log.md) | LLM observability in the UI: Grafana for trends/alerts + staff-console AI Operations (ops-admin) + customer-web dev overlay; `status.updated` and `... |
| [ADR-028](../docs/adr/ADR_Log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop BFF -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-029](../docs/adr/ADR_Log.md) | Agent output path: background turns (`POST /turns` 202); agent appends ADR-024 events to per-conversation Redis Stream; BFF pods read and forward; ... |
| [ADR-030](../docs/adr/ADR_Log.md) | Intent routing: cascade of rules -> fast in-process classifier -> economy-tier LLM classifier; clarify then handoff on low confidence; flow stickin... |
| [ADR-034](../docs/adr/ADR_Log.md) | RAG chunking: structure-aware per doc type, parent-child retrieval, context headers, metadata filters; sizes tuned with Ragas; applied to the ADR-0... |
| [ADR-036](../docs/adr/ADR_Log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-039](../docs/adr/ADR_Log.md) | Multi-format ingestion: detect by magic bytes -> parser plugin per format -> common Document model with provenance -> normalize, validate, clean, c... |
| [ADR-040](../docs/adr/ADR_Log.md) | Embeddings: bge-m3 in every environment via LiteLLM; `model_version` per vector; PII-masked queries; phase-3 bake-off; model change via blue/green ... |
