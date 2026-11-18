# buywise-deploy - local stack and runtime

Everything needed to run the system: Docker Compose stack (Postgres, Redis, Keycloak, LiteLLM), Keycloak realm and LiteLLM config as code, runtime scripts; later Helm charts and the kind cluster.

**Open in:** any editor (IntelliJ or VS Code); Docker/Compose support in JetBrains IDEs works on `compose/compose.yaml`.

## Contents
| Path | Purpose |
|---|---|
| `compose/compose.yaml` | The local stack |
| `compose/.env.example` | Settings template (copy to .env) |
| `../buywise-db/database/` | Creates the 4 databases and users (moved to buywise-db, ADR-046; compose mounts it) |
| `compose/keycloak/` | Realm as code |
| `compose/litellm/` | Model aliases and placeholder shadow prices |
| `scripts/benchmark_k.py` | Measures k |
| `local/scale.yaml` | S and measured k |
| `local/run-local.sh`, `local/stop-local.sh` | Start / stop the apps on the Mac (`make start`, `make stop`; moved from root `scripts/`, ADR-047) |
| `local/logs/` | App logs written by run-local.sh (git-ignored) |
| `Makefile` | env, up, down, ps, logs, k, demo-user |
| `../buywise-docs/08-buywise-deploy/` | 01-design.md, 02-learning.md (docs live in buywise-docs, ADR-048) |

## Run
`make up`, `make down`, `make ps`, `make logs`, `make k` (from the repo root or this folder).

## Documents
- [buywise-docs/08-buywise-deploy/01-design.md](../buywise-docs/08-buywise-deploy/01-design.md) - detailed design
- [buywise-docs/08-buywise-deploy/02-learning.md](../buywise-docs/08-buywise-deploy/02-learning.md) - learning notes per phase
- System overview: [buywise-docs/00-architecture-overview.md](../buywise-docs/00-architecture-overview.md); roadmap: [buywise-docs/09-implementation-roadmap.md](../buywise-docs/09-implementation-roadmap.md)

## Decisions that apply (central log: buywise-docs/10-adr/01-adr-log.md)
| ADR | Decision |
|---|---|
| [ADR-010](../buywise-docs/10-adr/01-adr-log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-013](../buywise-docs/10-adr/01-adr-log.md) | Local-first, small-scale runtime; production sizing via configuration only |
| [ADR-016](../buywise-docs/10-adr/01-adr-log.md) | Six deployables: web, services, agent, mcp, event-publisher, event-consumers |
| [ADR-017](../buywise-docs/10-adr/01-adr-log.md) | Envoy Gateway at the edge; no internal gateway; Spring Security in services; service mesh as future option |
| [ADR-026](../buywise-docs/10-adr/01-adr-log.md) | LLM metering and budgets: LiteLLM model gateway (pricing, spend, global budget, rate limits) + agent LLM client (per-turn/conversation/customer cap... |
| [ADR-035](../buywise-docs/10-adr/01-adr-log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-040](../buywise-docs/10-adr/01-adr-log.md) | Embeddings: bge-m3 in every environment via LiteLLM; `model_version` per vector; PII-masked queries; phase-3 bake-off; model change via blue/green ... |
