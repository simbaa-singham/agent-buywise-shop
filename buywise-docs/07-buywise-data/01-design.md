# Content and Test Data - Detailed Design

Part of [00-architecture-overview.md](../00-architecture-overview.md) - agent-buywise-shop. Status: Draft.
Databases, data model, backups and PII: [buywise-db design](../06-buywise-db/01-design.md) (design doc 06).

## 1. Purpose
What buywise-data provides and where it comes from: the knowledge documents the agent answers from, the eval sets, and the
generators (`buywise-data/tools/`) that also produce the seed JSON loaded by buywise-db (ADR-046, ADR-047).

| Folder | What | Used by |
|---|---|---|
| `knowledge/` | 103 knowledge documents in 11 formats (policies, notices, FAQ, guides, tables, training, notes, compatibility, generated) | `make ingest` (buywise-agent) |
| `eval/` | RAG, router, prompt-injection and price-leak eval sets | Agent evals |
| `inbox/` | Drop folder for new documents (runtime, git-ignored) | Ingestion pipeline (designed) |
| `tools/` | Generators: catalog, seed data, documents, evals (`make data`) | Writes `knowledge/`, `eval/` and `buywise-db/services/03-data/` |

## 2. Seed and test data (ADR-033)
| Data | Source | Notes |
|---|---|---|
| Products, variants, specs, list prices, compatibility | Curated real product lineup as our own JSON in `buywise-db/services/03-data/catalog/` (ADR-046); specs and prices verified by web search at generation; `specs_verified` date per product | Facts only; descriptions in our own wording; no source URLs; maker never named (`brand_id` only); no automated scraping |
| Images | None - placeholders only | No product images anywhere |
| Stores (~10), stock | Generated, fixed random seed | Includes out-of-stock and low-stock cases |
| Customers, orders, tickets | Faker, fixed random seed | Synthetic only; designed edge cases (delayed order, pickup ready, multi-order customer) |
| Eval sets | Built from the docs, reviewed | RAG (expected source chunks), router (ADR-030), prompt injection |

Loading: `make seed` runs buywise-db/services/02-dml/*.sql (ADR-046; explained in buywise-docs/07-buywise-data/03-walkthroughs/01-load-seed-data.md), `make ingest` (knowledge documents into pgvector; ingestion design in [buywise-agent rag](../03-buywise-agent/02-rag.md)). Same data on every machine and CI run.
