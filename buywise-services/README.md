# buywise-services

Business services: one Spring Boot 4.1 modular monolith (Spring Modulith) with modules catalog, inventory, order, customer, payment (mock), helpdesk. Owns business data and rules.

**Open in:** IntelliJ IDEA -> open `buywise-services/` (Gradle Kotlin DSL build added in phase 1, ADR-041; IntelliJ imports it and offers Run/Debug). Add `buywise-events/` to the same window in phase 4.

## Contents
| Path | Purpose |
|---|---|
| `src/main/resources/db/migration/` | Flyway migrations (V1 catalog, V2 inventory) |
| `Makefile` | migrate, flyway-info |
| `docs/` | design.md, learning.md |

## Run
`make migrate` (create/update tables), `make flyway-info` (applied / pending). Java code arrives in phase 1.

## Documents
- [docs/design.md](docs/design.md) - detailed design
- [docs/learning.md](docs/learning.md) - learning notes per phase
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-002](../docs/adr/ADR_Log.md) | Java for business services, Python for AI and MCP, TypeScript for UI/BFF |
| [ADR-010](../docs/adr/ADR_Log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-014](../docs/adr/ADR_Log.md) | One Spring Boot 4.1 modular monolith (Spring Modulith 2.x), controllers per use case |
| [ADR-041](../docs/adr/ADR_Log.md) | Gradle (Kotlin DSL) with a version catalog for all Java deployables (services, event publisher, event consumers) |
| [ADR-028](../docs/adr/ADR_Log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop BFF -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-032](../docs/adr/ADR_Log.md) | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j |
| [ADR-033](../docs/adr/ADR_Log.md) | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs (mu... |
| [ADR-035](../docs/adr/ADR_Log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-036](../docs/adr/ADR_Log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-037](../docs/adr/ADR_Log.md) | Conversation ownership owned by the helpdesk module in `buywise-services`; BFF caches in Redis; agent paused/resumed as second check |
