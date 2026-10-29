# Data and Databases - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Data ownership, storage choices and data model.

## 2. Stores
| Store | Use |
|---|---|
| PostgreSQL | Database per deployable (ADR-010), see table below |
| Redis | Semantic cache, rate limits, OTP codes, sessions (ADR-021), conversation event streams `conv:{id}` - delivery and replay, capped by count and time (ADR-024, ADR-029), token budget counters (ADR-026), conversation owner cache `conv:{id}:owner` (ADR-037) |
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
- helpdesk: `tickets` (assignee, status), `conversation_ownership` (conversation_id, owner bot/staff, staff_id, changed_at, changed_by) - ADR-037
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

## 4b. Backup policy (ADR-035) - design only, not run locally
| Data | Production design | Rationale |
|---|---|---|
| Postgres business cluster (`services`, `keycloak`) | Continuous WAL archiving + daily base backup to object storage (CloudNativePG Barman Cloud plugin); PITR window 30 days; weekly immutable copy to a separate account/region (object lock) | NFR 10: orders RPO 0 via sync replica, others RPO <= 5 min; immutable copy protects against ransomware and accidental deletion |
| Postgres AI cluster (`agent`, `litellm`, `langfuse`) | Same mechanism, PITR window 14 days | Lower criticality than orders |
| RAG index | In `agent` backups; also rebuildable via `make ingest` | Derived data |
| Redis | Not backed up | Ephemeral: sessions, streams, counters; loss = re-login + REST reload (docs/00 7.3); LiteLLM keeps spend in Postgres |
| Kafka | Not backed up; 3-broker replication; topic config as Strimzi CRDs in Git | Events originate in the Postgres outbox and can be replayed |
| Config (Keycloak realm, Helm values, dashboards) | As code in Git | Git is the backup |
| Restore drill | Monthly, timed against RTO 15 min | An untested backup is not a backup |
| Encryption | All backups encrypted at rest and in transit | Backups contain Confidential PII |

Local: no backups; all local data is reproducible from Git (`make seed`, `make ingest`).

## 4c. PII policy (ADR-036) - implemented locally
**Classification**
| Tier | Data | Rules |
|---|---|---|
| Restricted | OTP codes, session tokens, exchanged JWTs | Never in Postgres, logs or traces; OTPs hashed in Redis, 10 min TTL |
| Confidential PII | Name, email, phone, address; chat transcripts | Encrypted in transit and at rest; field-level encryption for email/phone/address; masked in logs/traces; access audited |
| Internal | Orders, tickets without direct identifiers | Normal access control |
| Public | Catalog, knowledge docs | None |

**Controls**
1. LLM prompts (A2): Microsoft Presidio detects PII in chat text before every LLM call and replaces it with reversible placeholders (`<EMAIL_1>`, `<PHONE_1>`, `<ADDRESS_1>`); the agent keeps the mapping in memory for the turn and restores real values in tool calls and the reply. Tools use handles (`address_id`, `order_id`) so the model never needs raw values. Never persisted: mapping is not written to checkpoints, logs or traces.
2. Field-level encryption (B2): email, phone and address encrypted in `buywise-services` with envelope encryption - per-record data keys encrypted by a master key (KMS in production; Kubernetes secret locally). Blind index (keyed HMAC of normalized email/phone) stored alongside for lookups (OTP verification, login match). Key rotation: re-wrap data keys under a new master key.
3. Logs, traces, metrics: masked before storage - masking in application code plus OTel Collector redaction processor as a safety net. `llm_calls` and AI Operations store/show masked text only.
4. Staff access: contact fields masked by default (`j***@e***.com`); "Reveal" shows full value and writes an audit record (who, when, reason). `ops-admin` sees masked transcripts only.
5. Least privilege: one database user per deployable (ADR-010); per-tool scopes (ADR-028).
6. Retention (NFR 11): transcripts 90 days then deleted/anonymized; logs 30 days; traces 14 days; orders 7 years with identity removable; profiles until account deletion; backups age out in 30 days (design only).
7. Privacy rights (US, e.g. CCPA/CPRA): export and deletion requests run as audited jobs started from the staff console. Deletion removes profile, conversations and tickets and anonymizes orders; backups age out within 30 days.

## 5. Open decisions
1. ~~Agent/knowledge data same database vs separate~~ - decided: separate `agent` database, AI cluster in production (ADR-010).
2. ~~Backup and PII policy~~ - decided: backups design only (ADR-035, section 4b); PII policy (ADR-036, section 4c). Retention set by NFR 11: chat transcripts 90 days then deleted/anonymized (includes `turns`, `llm_calls`), logs 30 days.
