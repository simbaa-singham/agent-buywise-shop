# deploy - local stack and runtime

Everything needed to run the system: Docker Compose stack (Postgres, Redis, Keycloak, LiteLLM), Keycloak realm and LiteLLM config as code, runtime scripts; later Helm charts and the kind cluster.

## Contents
| Path | Purpose |
|---|---|
| `compose/compose.yaml` | The local stack |
| `compose/.env.example` | Settings template (copy to .env) |
| `compose/postgres/init/` | Creates the 4 databases and users |
| `compose/keycloak/` | Realm as code |
| `compose/litellm/` | Model aliases and placeholder shadow prices |
| `scripts/benchmark_k.py` | Measures k |
| `local/scale.yaml` | S and measured k |
| `Makefile` | env, up, down, ps, logs, migrate, flyway-info, k |
| `docs/` | design.md, learning.md |

## Run
`make up`, `make down`, `make ps`, `make logs`, `make k` (from the repo root or this folder).

## Documents
- [docs/design.md](docs/design.md) - detailed design
- [docs/learning.md](docs/learning.md) - learning notes per phase
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-010](../docs/adr/ADR_Log.md) | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one... |
| [ADR-013](../docs/adr/ADR_Log.md) | Local-first, small-scale runtime; production sizing via configuration only |
| [ADR-016](../docs/adr/ADR_Log.md) | Six deployables: web, services, agent, mcp, event-publisher, event-consumers |
| [ADR-017](../docs/adr/ADR_Log.md) | Envoy Gateway at the edge; no internal gateway; Spring Security in services; service mesh as future option |
| [ADR-026](../docs/adr/ADR_Log.md) | LLM metering and budgets: LiteLLM model gateway (pricing, spend, global budget, rate limits) + agent LLM client (per-turn/conversation/customer cap... |
| [ADR-035](../docs/adr/ADR_Log.md) | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; R... |
| [ADR-040](../docs/adr/ADR_Log.md) | Embeddings: bge-m3 in every environment via LiteLLM; `model_version` per vector; PII-masked queries; phase-3 bake-off; model change via blue/green ... |
