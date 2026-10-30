# agent-buywise-shop

An AI shopping assistant that helps customers choose, order and track electronic devices.

Start here: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then [docs/00_Architecture_Overview.md](docs/00_Architecture_Overview.md)

Everything about a module lives inside it: `<module>/README.md`, `Makefile`, `docs/design.md`, `docs/learning.md`.

| Module | Deployable | Stack | Module README | Design |
|---|---|---|---|---|
| `buywise-web/` | buywise-web | Angular 22 + NestJS 11 (Fastify), Node.js 24 | [buywise-web](buywise-web/README.md) | [design](buywise-web/docs/design.md) |
| `buywise-services/` | buywise-services | Java 25, Spring Boot 4.1, Spring Modulith | [buywise-services](buywise-services/README.md) | [design](buywise-services/docs/design.md) |
| `buywise-agent/` | buywise-agent | Python 3.12, LangGraph 1.2, RAG | [buywise-agent](buywise-agent/README.md) | [design](buywise-agent/docs/design.md), [RAG](buywise-agent/docs/rag.md) |
| `buywise-mcp/` | buywise-mcp | Python, MCP Python SDK v2 | [buywise-mcp](buywise-mcp/README.md) | [design](buywise-mcp/docs/design.md) |
| `buywise-events/` | buywise-event-publisher, buywise-event-consumers | Java, Kafka | [buywise-events](buywise-events/README.md) | [design](buywise-events/docs/design.md) |
| `data/` | - | Seed data, knowledge documents, eval sets | [data](data/README.md) | [design](data/docs/design.md) |
| `deploy/` | - | Docker Compose, kind, Helm, GitHub Actions | [deploy](deploy/README.md) | [design](deploy/docs/design.md) |

**One repo, one editor per module.** All IDEs share this Git repo; each opens only its module folder:

| Editor | Open folder | Notes |
|---|---|---|
| WebStorm | `buywise-web/` | Angular + NestJS BFF + chat contract (npm workspaces; web and bff join in phase 1) |
| PyCharm | `buywise-agent/` + attach `buywise-mcp/` | Each with its own `.venv` interpreter, created by uv (ADR-042) |
| IntelliJ IDEA | `buywise-services/` (+ `buywise-events/` in phase 4) | Spring Boot / Java |
| Any (IntelliJ or VS Code) | repo root, `deploy/`, `data/`, `docs/` | Compose, data, cross-module docs |

Cross-module documents (`docs/`): [architecture overview](docs/00_Architecture_Overview.md), [decisions (ADR log)](docs/adr/ADR_Log.md), [roadmap](docs/09_Implementation_Roadmap.md), learning index: [Phase 0](docs/learning/Phase-0.md).

## Local quick start (phase 0)
Prerequisites: Docker, Node 24, uv (`brew install uv`; it installs Python 3.12 itself), Ollama running on the host with `qwen2.5:7b` and `bge-m3` pulled.

```bash
make data-tools agent-dev   # one-time: Python environments from uv.lock (commands delegate to module Makefiles)
make up                     # Postgres (+pgvector), Redis, Keycloak, LiteLLM
make migrate                # create the services tables (Flyway)
# load the seed data by hand: data/docs/walkthroughs/load-seed-data.md
make k                      # measure the LLM hardware factor k -> deploy/local/scale.yaml
make test                   # contract tests + lint
make help                   # all targets
```
