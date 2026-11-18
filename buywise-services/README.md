# buywise-services

Business services: one Spring Boot 4.1 modular monolith (Spring Modulith) with modules catalog, inventory, order, customer, payment (mock), helpdesk. Owns business data and rules.

**Open in:** IntelliJ IDEA -> open `buywise-services/` (Gradle Kotlin DSL build added in phase 1, ADR-041; IntelliJ imports it and offers Run/Debug). Add `buywise-events/` to the same window in phase 4.

## Contents
| Path | Purpose |
|---|---|
| `../buywise-db/services/01-ddl/` | Flyway migrations V1-V4 - live in buywise-db (ADR-046); Gradle packs them into the app at `db/migration` |
| `Makefile` | migrate, flyway-info |
| `../buywise-docs/buywise-services/` | design.md, learning.md (docs live in buywise-docs, ADR-048) |

## Run
`make migrate` (create/update tables), `make flyway-info` (applied / pending). Java code arrives in phase 1.

## Documents
- [buywise-docs/buywise-services/design.md](../buywise-docs/buywise-services/design.md) - detailed design
- [buywise-docs/buywise-services/learning.md](../buywise-docs/buywise-services/learning.md) - learning notes per phase
- System overview: [buywise-docs/00_Architecture_Overview.md](../buywise-docs/00_Architecture_Overview.md); roadmap: [buywise-docs/09_Implementation_Roadmap.md](../buywise-docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: buywise-docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-002](../buywise-docs/adr/ADR_Log.md) | Java for business services, Python for AI and MCP, TypeScript for UI/Node server |
| [ADR-010](../buywise-docs/adr/ADR_Log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-014](../buywise-docs/adr/ADR_Log.md) | One Spring Boot 4.1 modular monolith (Spring Modulith 2.x), controllers per use case |
| [ADR-043](../buywise-docs/adr/ADR_Log.md) | Product `availability` = sale status only (`available` / `preorder` / `discontinued`), DB CHECK + contract enum; stock only from inventory |
| [ADR-041](../buywise-docs/adr/ADR_Log.md) | Gradle (Kotlin DSL) with a version catalog for all Java deployables (services, event publisher, event consumers) |
| [ADR-028](../buywise-docs/adr/ADR_Log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop Node server -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-032](../buywise-docs/adr/ADR_Log.md) | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j |
| [ADR-033](../buywise-docs/adr/ADR_Log.md) | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs (mu... |
| [ADR-035](../buywise-docs/adr/ADR_Log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-036](../buywise-docs/adr/ADR_Log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-037](../buywise-docs/adr/ADR_Log.md) | Conversation ownership owned by the helpdesk module in `buywise-services`; Node server caches in Redis; agent paused/resumed as second check |
