# data - seed data, knowledge documents, eval sets

All project data: the product catalog, synthetic stores/customers/orders/tickets, 103 knowledge documents in 11 formats, eval sets, and the tools that generate them.

**Open in:** any editor (IntelliJ or VS Code) for data files; PyCharm if you work on the generators in `tools/` (interpreter `data/tools/.venv`).

## Contents
| Path | Purpose |
|---|---|
| `seed/` | Catalog JSON and synthetic business data |
| `knowledge/` | Knowledge documents (DOCX, PDF, scans, HTML, XLSX, CSV, PPTX, EML, Markdown, TXT) |
| `eval/` | RAG, router, prompt-injection, price-leak eval sets |
| `tools/` | Generators (catalog, seed, documents, evals) |
| `docs/walkthroughs/` | Manual seed-data load (explained + one SQL file) |
| `Makefile` | tools, generate |
| `docs/` | design.md, learning.md |

## Run
`make data-tools` once, then `make data` to regenerate. Loading into Postgres is manual: docs/walkthroughs/load-seed-data.md.

## Documents
- [docs/design.md](docs/design.md) - detailed design
- [docs/learning.md](docs/learning.md) - learning notes per phase
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-010](../docs/adr/ADR_Log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-011](../docs/adr/ADR_Log.md) | Postgres + pgvector + full-text for RAG (hybrid, RRF, rerank); retriever interface; `pg_search` BM25 upgrade path; RAG reads off the primary in pro... |
| [ADR-033](../docs/adr/ADR_Log.md) | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs (mu... |
| [ADR-034](../docs/adr/ADR_Log.md) | RAG chunking: structure-aware per doc type, parent-child retrieval, context headers, metadata filters; sizes tuned with Ragas; applied to the ADR-0... |
| [ADR-035](../docs/adr/ADR_Log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-036](../docs/adr/ADR_Log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-039](../docs/adr/ADR_Log.md) | Multi-format ingestion: detect by magic bytes -> parser plugin per format -> common Document model with provenance -> normalize, validate, clean, c... |
