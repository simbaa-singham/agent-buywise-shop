# buywise-services

Business services: one Spring Boot 4.1 modular monolith (Spring Modulith). Built modules: catalog, inventory, customers, orders; designed for later: payment (mock), helpdesk. Owns business data and rules.

**Open in:** IntelliJ IDEA -> open `buywise-services/` (Gradle Kotlin DSL build, ADR-041; IntelliJ imports it and offers Run/Debug). Add `buywise-events/` to the same window in phase 4.

## Contents
| Path | Purpose |
|---|---|
| `src/main/java/com/buywise/services/` | One package per module: `catalog/`, `inventory/`, `customers/`, `orders/` (controller + service + records) |
| `src/main/resources/application.yaml` | Port 8081, database `services`, Flyway settings |
| `src/test/java/.../ModularityTest.java` | Spring Modulith check that modules only use each other's public API |
| `build.gradle.kts`, `settings.gradle.kts`, `gradle/libs.versions.toml` | Gradle build and version catalog (ADR-041); the build packs `../buywise-db/services/01-ddl/` into the app at `db/migration` (ADR-046) |
| `scripts/try-apis.sh` | One curl per REST API |
| `Makefile` | build, run, migrate, flyway-info |
| `../buywise-docs/02-buywise-services/` | 01-design.md, 02-learning.md (docs live in buywise-docs, ADR-048) |

Tables and seed data for this app are in `buywise-db/services/` (ADR-046), not here.

## Run
`make -C buywise-services build` (compile + tests), `make -C buywise-services run` -> http://localhost:8081/api (needs `make up` and `make migrate`; `make seed` for data). `./scripts/try-apis.sh` calls each API once. `make start` runs it with everything else.

## Documents
- [buywise-docs/02-buywise-services/01-design.md](../buywise-docs/02-buywise-services/01-design.md) - detailed design
- [buywise-docs/02-buywise-services/02-learning.md](../buywise-docs/02-buywise-services/02-learning.md) - learning notes per phase
- System overview: [buywise-docs/00-architecture-overview.md](../buywise-docs/00-architecture-overview.md); roadmap: [buywise-docs/09-implementation-roadmap.md](../buywise-docs/09-implementation-roadmap.md)

## Decisions that apply (central log: buywise-docs/10-adr/01-adr-log.md)
| ADR | Decision |
|---|---|
| [ADR-002](../buywise-docs/10-adr/01-adr-log.md) | Java for business services, Python for AI and MCP, TypeScript for UI/Node server |
| [ADR-010](../buywise-docs/10-adr/01-adr-log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-014](../buywise-docs/10-adr/01-adr-log.md) | One Spring Boot 4.1 modular monolith (Spring Modulith 2.x), controllers per use case |
| [ADR-043](../buywise-docs/10-adr/01-adr-log.md) | Product `availability` = sale status only (`available` / `preorder` / `discontinued`), DB CHECK + contract enum; stock only from inventory |
| [ADR-041](../buywise-docs/10-adr/01-adr-log.md) | Gradle (Kotlin DSL) with a version catalog for all Java deployables (services, event publisher, event consumers) |
| [ADR-028](../buywise-docs/10-adr/01-adr-log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop Node server -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-032](../buywise-docs/10-adr/01-adr-log.md) | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j |
| [ADR-033](../buywise-docs/10-adr/01-adr-log.md) | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs (mu... |
| [ADR-035](../buywise-docs/10-adr/01-adr-log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-036](../buywise-docs/10-adr/01-adr-log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-037](../buywise-docs/10-adr/01-adr-log.md) | Conversation ownership owned by the helpdesk module in `buywise-services`; Node server caches in Redis; agent paused/resumed as second check |
