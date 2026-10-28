# Data and Databases - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Data ownership, storage choices and data model.

## 2. Stores
| Store | Use |
|---|---|
| PostgreSQL | One database: business data (schema per module), Spring Modulith event publication tables, conversations, agent checkpoints, vectors (pgvector) |
| Redis | Semantic cache, rate limits, OTP codes, sessions (ADR-021), chat event replay streams (ADR-024), token budget counters (ADR-026) |
| Kafka | Event log (see 06) |

## 3. Data ownership
Each module of `buywise-services` owns its schema; no cross-module joins; other deployables read via REST API or events.

## 4. Data model (initial)
- customer: `customers`
- catalog: `products`, `variants`, `compatibility`
- inventory: `inventory`, `reservations`
- order: `carts`, `cart_items`, `orders`, `order_items`, `shipments`, `pickups`
- helpdesk: `tickets`
- agent: `conversations`, `messages`, checkpoints, `turns` (per-turn totals: latency, tokens, cost), `llm_calls` (one row per LLM call: turn, stage, model, TTFT, duration, tokens in/out, tokens/sec, cost, budget event) - ADR-026/027
- knowledge: `documents`, `chunks` (with embeddings)

## 5. Open decisions
1. Agent/knowledge data in the same database (separate schemas) vs a separate database.
2. Backup and PII policy. Retention set by NFR 8: chat transcripts 90 days then deleted/anonymized (includes `turns`, `llm_calls`), logs 30 days.
