# Data and Databases - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Data ownership, storage choices and data model.

## 2. Stores
| Store | Use |
|---|---|
| PostgreSQL | Database per deployable (ADR-010), see table below |
| Redis | Semantic cache, rate limits, OTP codes, sessions (ADR-021), conversation event streams `conv:{id}` - delivery and replay, capped by count and time (ADR-024, ADR-029), token budget counters (ADR-026) |
| Kafka | Event log (see 06) |

**PostgreSQL databases (ADR-010):**
| Database | Owner | Schemas / contents | Production cluster |
|---|---|---|---|
| `services` | `buywise-services` | one schema per module (catalog, inventory, order, customer, payment, helpdesk) + Spring Modulith event publication tables | Business (synchronous replica, RPO 0) |
| `keycloak` | Keycloak | Keycloak's own tables | Business |
| `agent` | `buywise-agent` | `agent` (conversations, messages, checkpoints, turns, llm_calls); `knowledge` (documents, chunks + pgvector) | AI (read replica serves RAG reads, ADR-011) |
| `litellm` | LiteLLM | spend and budget tables | AI |
| `langfuse` | Langfuse | Langfuse's Postgres tables (v3 also needs ClickHouse, Redis, object storage - see docs/08 open decision 2) | AI |

- Each database has its own Postgres user with access only to that database.
- Local: one CloudNativePG cluster hosts all databases with the same names and users; the production split is connection strings only.

## 3. Data ownership
Each module of `buywise-services` owns its schema; no cross-module joins; other deployables read via REST API or events.

## 4. Data model (initial)
- customer: `customers`
- catalog: `products`, `variants`, `compatibility`
- inventory: `inventory`, `reservations`
- order: `carts`, `cart_items`, `orders`, `order_items`, `shipments`, `pickups`
- helpdesk: `tickets`
- agent: `conversations`, `messages`, checkpoints, `turns` (per-turn totals: latency, tokens, cost), `llm_calls` (one row per LLM call: turn, stage, model, TTFT, duration, tokens in/out, tokens/sec, cost, budget event) - ADR-026/027, `router_decisions` (turn, tier, intents, confidence, latency, clarified/handoff) - ADR-030
- knowledge: `documents` (doc_type, version, content hash, front matter), `chunks` (embedding, full-text vector, `parent_id` for parent-child retrieval, metadata columns per ADR-034)
- catalog products carry `brand_id` (opaque id, never displayed) and `specs_verified` date; no images (placeholders only)

## 4a. Seed and test data (ADR-033)
| Data | Source | Notes |
|---|---|---|
| Products, variants, specs, list prices, compatibility | Curated real product lineup as our own JSON in `data/seed/catalog/{category}/`; specs and prices verified by web search at generation; `specs_verified` date per product | Facts only; descriptions in our own wording; no source URLs; maker never named (`brand_id` only); no automated scraping |
| Images | None - placeholders only | No product images anywhere |
| Stores (~10), stock | Generated, fixed random seed | Includes out-of-stock and low-stock cases |
| Customers, orders, tickets | Faker, fixed random seed | Synthetic only; designed edge cases (delayed order, pickup ready, multi-order customer) |
| Eval sets | Built from the docs, reviewed | RAG (expected source chunks), router (ADR-030), prompt injection |

Loading: `make seed` (Postgres via `buywise-services` seed migrations/job), `make ingest` (RAG pipeline). Same data on every machine and CI run.

## 5. Open decisions
1. ~~Agent/knowledge data same database vs separate~~ - decided: separate `agent` database, AI cluster in production (ADR-010).
2. Backup and PII policy. Retention set by NFR 8: chat transcripts 90 days then deleted/anonymized (includes `turns`, `llm_calls`), logs 30 days.
