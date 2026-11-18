# buywise-data - knowledge documents, eval sets, generators

Shared content and test data (ADR-047): 103 knowledge documents in 11 formats, eval sets, and the tools that generate them. The tools also generate the product catalog and synthetic stores/customers/orders/tickets, written as seed JSON to `buywise-db/services/03-data/` (ADR-046).

**Open in:** any editor (IntelliJ or VS Code) for data files; PyCharm if you work on the generators in `tools/` (interpreter `buywise-data/tools/.venv`, created by uv from `tools/pyproject.toml` + `tools/uv.lock`, ADR-042).

## Contents
| Path | Purpose |
|---|---|
| `knowledge/` | Knowledge documents (DOCX, PDF, scans, HTML, XLSX, CSV, PPTX, EML, Markdown, TXT) |
| `eval/` | RAG, router, prompt-injection, price-leak eval sets |
| `tools/` | Generators (catalog, seed, documents, evals); catalog + seed JSON is written to `buywise-db/services/03-data/` (ADR-046) |
| `../buywise-docs/buywise-data/walkthroughs/` | Seed-data load explained step by step (scripts in `buywise-db/services/02-dml/`) |
| `Makefile` | tools, generate |
| `../buywise-docs/buywise-data/` | design.md, learning.md (docs live in buywise-docs, ADR-048) |

## Run
Needs uv (`brew install uv`). `make data-tools` once, then `make data` to regenerate. Loading into Postgres: `make seed` (SQL in buywise-db/services/02-dml, JSON in buywise-db/services/03-data; explained in docs/walkthroughs/load-seed-data.md).

## Documents
- [buywise-docs/buywise-data/design.md](../buywise-docs/buywise-data/design.md) - detailed design
- [buywise-docs/buywise-data/learning.md](../buywise-docs/buywise-data/learning.md) - learning notes per phase
- System overview: [buywise-docs/00_Architecture_Overview.md](../buywise-docs/00_Architecture_Overview.md); roadmap: [buywise-docs/09_Implementation_Roadmap.md](../buywise-docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: buywise-docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-010](../buywise-docs/adr/ADR_Log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-011](../buywise-docs/adr/ADR_Log.md) | Postgres + pgvector + full-text for RAG (hybrid, RRF, rerank); retriever interface; `pg_search` BM25 upgrade path; RAG reads off the primary in pro... |
| [ADR-033](../buywise-docs/adr/ADR_Log.md) | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs (mu... |
| [ADR-034](../buywise-docs/adr/ADR_Log.md) | RAG chunking: structure-aware per doc type, parent-child retrieval, context headers, metadata filters; sizes tuned with Ragas; applied to the ADR-0... |
| [ADR-035](../buywise-docs/adr/ADR_Log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-036](../buywise-docs/adr/ADR_Log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-039](../buywise-docs/adr/ADR_Log.md) | Multi-format ingestion: detect by magic bytes -> parser plugin per format -> common Document model with provenance -> normalize, validate, clean, c... |
