# buywise-events (event publisher and consumers)

Kafka event publisher (committed business events) and event consumers (notifications, projections, staff console updates). Several design decisions are still open.

**Open in:** IntelliJ IDEA -> added to the `buywise-services/` window (Gradle Kotlin DSL build added in phase 4, ADR-041).

## Contents
| Path | Purpose |
|---|---|
| `publisher/, consumers/` | Built in phase 4 |
| `../buywise-docs/05-buywise-events/` | 01-design.md (docs live in buywise-docs, ADR-048) |

## Run
Built in phase 4.

## Documents
- [buywise-docs/05-buywise-events/01-design.md](../buywise-docs/05-buywise-events/01-design.md) - detailed design
- System overview: [buywise-docs/00-architecture-overview.md](../buywise-docs/00-architecture-overview.md); roadmap: [buywise-docs/09-implementation-roadmap.md](../buywise-docs/09-implementation-roadmap.md)

## Decisions that apply (central log: buywise-docs/10-adr/01-adr-log.md)
| ADR | Decision |
|---|---|
| [ADR-009](../buywise-docs/10-adr/01-adr-log.md) |  |
| [ADR-016](../buywise-docs/10-adr/01-adr-log.md) | Six deployables: web, services, agent, mcp, event-publisher, event-consumers |
