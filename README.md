# agent-buywise-shop

An AI shopping assistant that helps customers choose, order and track electronic devices.

Start here: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then [docs/00_Architecture_Overview.md](docs/00_Architecture_Overview.md)

Everything about a module lives inside it: `<module>/README.md`, `Makefile`, `docs/design.md`, `docs/learning.md`.

| Module | Deployable | Stack | Module README | Design |
|---|---|---|---|---|
| `ui/` | buywise-web | Angular 22 + NestJS 11 (Fastify), Node.js 24 | [ui](ui/README.md) | [design](ui/docs/design.md) |
| `services/` | buywise-services | Java 25, Spring Boot 4.1, Spring Modulith | [services](services/README.md) | [design](services/docs/design.md) |
| `agent/` | buywise-agent | Python 3.12, LangGraph 1.2, RAG | [agent](agent/README.md) | [design](agent/docs/design.md), [RAG](agent/docs/rag.md) |
| `mcp/` | buywise-mcp | Python, MCP Python SDK v2 | [mcp](mcp/README.md) | [design](mcp/docs/design.md) |
| `events/` | buywise-event-publisher, buywise-event-consumers | Java, Kafka | [events](events/README.md) | [design](events/docs/design.md) |
| `data/` | - | Seed data, knowledge documents, eval sets | [data](data/README.md) | [design](data/docs/design.md) |
| `deploy/` | - | Docker Compose, kind, Helm, GitHub Actions | [deploy](deploy/README.md) | [design](deploy/docs/design.md) |

Cross-module documents (`docs/`): [architecture overview](docs/00_Architecture_Overview.md), [decisions (ADR log)](docs/adr/ADR_Log.md), [roadmap](docs/09_Implementation_Roadmap.md), learning index: [Phase 0](docs/learning/Phase-0.md).

## Local quick start (phase 0)
Prerequisites: Docker, Node 24, Python 3.12+, Ollama running on the host with `qwen2.5:7b` and `bge-m3` pulled.

```bash
make data-tools agent-dev   # one-time: Python tool environments (commands delegate to module Makefiles)
make up                     # Postgres (+pgvector), Redis, Keycloak, LiteLLM
make migrate                # create the services tables (Flyway)
# load the seed data by hand: data/docs/walkthroughs/load-seed-data.md
make k                      # measure the LLM hardware factor k -> deploy/local/scale.yaml
make test                   # contract tests + lint
make help                   # all targets
```
