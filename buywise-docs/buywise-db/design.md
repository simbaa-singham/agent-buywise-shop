# Databases and Data Stores - Detailed Design

Part of [00_Architecture_Overview.md](../00_Architecture_Overview.md) (design doc 07) - agent-buywise-shop. Status: Draft.
Scripts and seed data: [buywise-db/README.md](../../buywise-db/README.md) (ADR-046). Seed data sources: [buywise-data design](../buywise-data/design.md).

## 1. Purpose
Data stores, database ownership, data model, backups and PII rules. (Split from the buywise-data design on 2026-11-18: databases belong to buywise-db.)

## 2. Stores
| Store | Use |
|---|---|
| PostgreSQL | Database per deployable (ADR-010), see table below |
| Redis | Semantic cache, rate limits, OTP codes, sessions (ADR-021), conversation event streams `conv:{id}` - delivery and replay, capped by count and time (ADR-024, ADR-029), token budget counters (ADR-026), conversation owner cache `conv:{id}:owner` (ADR-037) |
| Kafka | Event log (see [06](../buywise-events/design.md)) |

**PostgreSQL databases (ADR-010):**
| Database | Owner | Schemas / contents | Production cluster |
|---|---|---|---|
| `services` | `buywise-services` | one schema per module (catalog, inventory, order, customer, payment, helpdesk) + Spring Modulith event publication tables | Business (synchronous replica, RPO 0) |
| `keycloak` | Keycloak | Keycloak's own tables | Business |
| `agent` | `buywise-agent` | `agent` (conversations, messages, checkpoints, turns, llm_calls); `knowledge` (documents, chunks + pgvector) - built today as `rag.chunks` | AI (read replica serves RAG reads, ADR-011) |
| `litellm` | LiteLLM | spend and budget tables | AI |
| `langfuse` | Langfuse | Langfuse's Postgres tables (v3 also needs ClickHouse, Redis, object storage - see buywise-docs/buywise-deploy/design.md open decision 2) | AI |

- Each database has its own Postgres user with access only to that database.
- Local: one CloudNativePG cluster hosts all databases with the same names and users; the production split is connection strings only. Today (Docker Compose) one Postgres container; `buywise-db/database/01-databases.sh` creates the databases and users on its first start.

## 3. Data ownership
Each module of `buywise-services` owns its schema; no cross-module joins; other deployables read via REST API or events.

## 4. Data model

**Built today** (local end-to-end build; DDL in `buywise-db`, ADR-046):
| Database | Schema | Tables | DDL |
|---|---|---|---|
| `services` | `catalog` | `products`, `variants`, `price_history`, `compatibility` | `buywise-db/services/01-ddl/V1`, `V3` |
| `services` | `inventory` | `stores`, `stock` | `V2` |
| `services` | `customers` | `customers` | `V4` |
| `services` | `orders` | `sales_tax`, `orders`, `order_items` (+ sequence `order_number_seq`) | `V4` |
| `services` | `flyway` | `flyway_schema_history` | Flyway |
| `agent` | `rag` | `chunks` (embedding `vector(1024)`, HNSW index) | `buywise-db/agent/V1__rag.sql` |
| `agent` | `flyway` | `flyway_schema_history` | Flyway |

**Designed** (initial target; not all built):
- customer: `customers`
- catalog: `products`, `variants`, `compatibility`
- inventory: `inventory`, `reservations`
- order: `carts`, `cart_items`, `orders`, `order_items`, `shipments`, `pickups`
- helpdesk: `tickets` (assignee, status), `conversation_ownership` (conversation_id, owner bot/staff, staff_id, changed_at, changed_by) - ADR-037
- agent: `conversations`, `messages`, checkpoints, `turns` (per-turn totals: latency, tokens, cost), `llm_calls` (one row per LLM call: turn, stage, model, TTFT, duration, tokens in/out, tokens/sec, cost, budget event) - ADR-026/027, `router_decisions` (turn, tier, intents, confidence, latency, clarified/handoff) - ADR-030
- knowledge: `documents` (doc_type, version, content hash, detected format, parser + parser version, parse status, quarantine reason, parse metrics, metadata), `document_elements` (type, order, text/table/record, provenance: page+bbox / sheet!row / slide / DOM path / attachment) - ADR-039, `chunks` (embedding `vector(1024)` + `model_version` (ADR-040), full-text vector, `parent_id` for parent-child retrieval, metadata columns per ADR-034)
- catalog products carry `brand_id` (opaque id, never displayed) and `specs_verified` date; no images (placeholders only)

## 5. Backup policy (ADR-035) - design only, not run locally
| Data | Production design | Rationale |
|---|---|---|
| Postgres business cluster (`services`, `keycloak`) | Continuous WAL archiving + daily base backup to object storage (CloudNativePG Barman Cloud plugin); PITR window 30 days; weekly immutable copy to a separate account/region (object lock) | NFR 10: orders RPO 0 via sync replica, others RPO <= 5 min; immutable copy protects against ransomware and accidental deletion |
| Postgres AI cluster (`agent`, `litellm`, `langfuse`) | Same mechanism, PITR window 14 days | Lower criticality than orders |
| RAG index | In `agent` backups; also rebuildable via `make ingest` | Derived data |
| Redis | Not backed up | Ephemeral: sessions, streams, counters; loss = re-login + REST reload (buywise-docs/00 7.3); LiteLLM keeps spend in Postgres |
| Kafka | Not backed up; 3-broker replication; topic config as Strimzi CRDs in Git | Events originate in the Postgres outbox and can be replayed |
| Config (Keycloak realm, Helm values, dashboards) | As code in Git | Git is the backup |
| Restore drill | Monthly, timed against RTO 15 min | An untested backup is not a backup |
| Encryption | All backups encrypted at rest and in transit | Backups contain Confidential PII |

Local: no backups; all local data is reproducible from Git (`make migrate`, `make seed`, `make ingest`).

## 6. PII policy (ADR-036) - implemented locally
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

## 7. Open decisions
1. ~~Agent/knowledge data same database vs separate~~ - decided: separate `agent` database, AI cluster in production (ADR-010).
2. ~~Backup and PII policy~~ - decided: backups design only (ADR-035, section 5); PII policy (ADR-036, section 6). Retention set by NFR 11: chat transcripts 90 days then deleted/anonymized (includes `turns`, `llm_calls`), logs 30 days.
