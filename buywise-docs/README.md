# buywise-docs

Every document of the project (ADR-048), numbered in reading order: folders and files start at 00, files inside each folder at 01.

| # | Document | What |
|---|---|---|
| 00 | [00-architecture-overview.md](00-architecture-overview.md) | Requirements, NFRs, architecture, deployables, repository layout |
| 01 | [01-buywise-web/](01-buywise-web/) | [design](01-buywise-web/01-design.md), [learning](01-buywise-web/02-learning.md) - Angular app + Node server |
| 02 | [02-buywise-services/](02-buywise-services/) | [design](02-buywise-services/01-design.md), [learning](02-buywise-services/02-learning.md) - business services (Java) |
| 03 | [03-buywise-agent/](03-buywise-agent/) | [design](03-buywise-agent/01-design.md), [RAG](03-buywise-agent/02-rag.md), [learning](03-buywise-agent/03-learning.md) - LangGraph agent |
| 04 | [04-buywise-mcp/](04-buywise-mcp/) | [design](04-buywise-mcp/01-design.md), [learning](04-buywise-mcp/02-learning.md) - MCP tool servers |
| 05 | [05-buywise-events/](05-buywise-events/) | [design](05-buywise-events/01-design.md) - Kafka publisher and consumers (not built) |
| 06 | [06-buywise-db/](06-buywise-db/) | [design](06-buywise-db/01-design.md) - databases, data model, backups, PII; scripts in [buywise-db](../buywise-db/README.md) |
| 07 | [07-buywise-data/](07-buywise-data/) | [design](07-buywise-data/01-design.md), [learning](07-buywise-data/02-learning.md), [seed-data load walkthrough](07-buywise-data/03-walkthroughs/01-load-seed-data.md) - content and test data |
| 08 | [08-buywise-deploy/](08-buywise-deploy/) | [design](08-buywise-deploy/01-design.md), [learning](08-buywise-deploy/02-learning.md) - local stack, later Kubernetes |
| 09 | [09-implementation-roadmap.md](09-implementation-roadmap.md) | Phases, what is built, simplifications to revisit |
| 10 | [10-adr/01-adr-log.md](10-adr/01-adr-log.md) | All architecture decisions |
| 11 | [11-learning/](11-learning/) | [phase 0](11-learning/01-phase-0-foundations.md), [phase 1 local end to end](11-learning/02-phase-1-local-end-to-end.md), [deep-dive week](11-learning/03-deep-dive-week.md) |
| 12 | [12-archive/](12-archive/) | Earlier designs, kept for history |

Each module folder in the repo keeps its own README.md (what it is, how to run it, which ADRs apply).
