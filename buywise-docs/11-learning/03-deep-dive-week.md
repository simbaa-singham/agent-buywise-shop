# Deep-dive week (from 2026-11-16) - one area per day, 2 hours each

Goal: understand the whole project from scratch - why each part exists, how it is built, and how to run and change it.
Each day: 30 min concepts -> 60 min code walkthrough -> 30 min hands-on (run, break, fix) + questions.
Notes from each day go into that module's buywise-docs/NN-<module>/0N-learning.md.

| Day | Date | Area | Concepts | Code / docs | Hands-on |
|---|---|---|---|---|---|
| 1 | Mon 11-16 | Requirements and design | What the product does, actors, use cases, NFRs and S/k scaling, 6 deployables, layers, the 3 paths (chat, screen, event), key ADRs | buywise-docs/00, buywise-docs/09, ADR log | `make start`, one chat end to end, map each step to a deployable |
| 2 | Tue 11-17 | Data and infrastructure | Docker Compose, Postgres database-per-deployable + schemas, Flyway, Redis, Keycloak, seed data, event contracts | buywise-deploy/, data/, migrations V1-V4, contracts | Query the tables in pgAdmin, run contract tests, break one example |
| 3 | Wed 11-18 | buywise-services (Java) | Spring Boot, modular monolith (Spring Modulith), JdbcClient, records, REST, error handling, transactions | catalog, inventory, customers, orders | try-apis.sh, place + cancel an order, watch stock change |
| 4 | Thu 11-19 | buywise-mcp (Python) | What MCP is, tools vs REST, tool descriptions as prompts, identity never a tool argument | 3 MCP servers | Call tools with an MCP client, change a tool description |
| 5 | Fri 11-20 | buywise-agent part 1: agent loop | LLM, tool calling, LangGraph graph/state/nodes, LiteLLM + Ollama, Redis Stream events, quote-then-yes | graph, nodes, events | Follow one turn in the logs, watch the Redis Stream |
| 6 | Sat 11-21 | buywise-agent part 2: RAG | Embeddings (bge-m3), chunking, pgvector + full-text hybrid search, citations, ingest rules | ingest, search | Ingest docs, run a search, ask a policy question |
| 7 | Sun 11-22 | buywise-web + full trace | Angular (signals, SignalStore), Node server (NestJS), session, Keycloak login, SSE + replay | server/, web/ | Login, chat, kill the SSE mid-reply, trace one message browser -> DB -> browser |

After day 7: pick the next feature (staff console + handoff, Kafka order events, more document formats, budgets/guardrails, or polish).

---

## Day 1 notes - Requirements and design

### Requirements
- Customer can: choose (discover, compare, configure), order (stock, quote, confirm, delivery or pickup), track (status, cancel while allowed), ask (policies, warranty, hours - answered with a citation), reach a human.
- Out of scope: returns, exchanges, refunds, trade-ins, voice, real payments (mock).
- Actors: customer (chat), store staff (console, not built yet), Keycloak (login), LLM (via LiteLLM; Ollama locally), payment and shipping (mock).
- Trust rules: prices, stock and status only from tool results; identity never a tool argument; order = quote, then "yes"; knowledge answers cite a source.
- NFRs: production targets; local = same system scaled by S = 40 (volume) and k ~ 2.8 (LLM speed). Non-LLM latency, error rates, security, correctness same as production. Every limit has a defined fallback (buywise-docs/00 section 7.3).

### Design
Layers - each talks only to the one below:
```
Browser -> [1] Envoy (design only) -> [2] buywise-web :3000 -> [3] buywise-agent :8000
        -> [4] buywise-mcp :8090 -> [5] buywise-services :8081 -> [7] Postgres / Redis / Keycloak / LiteLLM -> Ollama
[6] Kafka publisher + consumers: not built yet
```
Three paths:
- Chat: browser -> Node server -> agent `POST /turns` (202) -> LLM + MCP tools -> services -> Postgres; agent writes events to Redis Stream `conv:{id}`; Node server reads it and sends SSE to the browser. A dropped stream resumes from `Last-Event-ID`.
- Screen: browser -> Node server -> services REST (no AI).
- Event (not built): services writes state + outbox record in one transaction -> publisher -> Kafka -> consumers.

Decisions that shape everything: tools are the only source of facts; identity by login (designed token exchange, built as `X-Customer-Id` header); all LLM calls via LiteLLM; one Postgres with a database per deployable and pgvector inside; one JSON Schema chat contract; order placed by code on "yes", not by the model.
Designed vs built today: buywise-docs/09 section 4.

### Technology stack and its use
| Layer | Technology | Used for |
|---|---|---|
| Web | Angular 22 | Chat page |
| Web | Angular Material + CDK | UI components, accessibility |
| Web | NgRx SignalStore | Chat state, fed by the SSE stream |
| Web | marked | Renders Markdown replies |
| Web | NestJS 12 + Fastify (Node.js 24, TypeScript) | Node server: login, session, chat API, SSE, serves the Angular build |
| Web | ioredis | Sessions and reading reply streams in Redis |
| Business | Java 25, Spring Boot 4.1 (Web MVC) | REST APIs: products, stock, customers, orders |
| Business | Spring Modulith | Module boundaries inside one app, checked by a test |
| Business | Spring JDBC (JdbcClient) | Plain SQL mapped to Java records |
| Business | Bean Validation | Request checks |
| Business | Flyway | Database migrations V1-V4 |
| Business | Actuator | Health endpoint |
| Business | Gradle (Kotlin DSL) | Build, version catalog |
| Tools | MCP Python SDK v2 | Tools the AI can call (search, stock, quote/place/cancel) |
| Tools | Starlette + uvicorn | Hosts `/mcp/catalog`, `/mcp/inventory`, `/mcp/orders` |
| Tools | httpx | Calls services REST |
| AI | LangGraph | Agent loop as a graph (LLM -> tools -> LLM ...) and state |
| AI | langchain-openai | Talks to LiteLLM (OpenAI-compatible API) |
| AI | MCP client | Calls buywise-mcp tools |
| AI | FastAPI + uvicorn | `POST /turns` |
| AI | psycopg + pgvector, numpy | Knowledge chunks and vector search in Postgres |
| AI | redis | Writes reply events to Redis Streams |
| AI | pypdf, python-docx, beautifulsoup4, pyyaml | Read knowledge documents for RAG ingest |
| AI | pydantic, uv | Typed settings and contract models; locked dependencies |
| Platform | PostgreSQL 17 + pgvector | All databases (one per deployable) and vectors |
| Platform | Redis 7.4 | Sessions, conversation reply streams |
| Platform | Keycloak 26 | Customer login (OpenID Connect) |
| Platform | LiteLLM | Model gateway: `buywise-primary` -> real model; cost metering later |
| Platform | Ollama (on the Mac) | qwen2.5:7b (chat), bge-m3 (embeddings) |
| Platform | Flyway container, Docker Compose | Run migrations; run the stack |
| Cross-module | JSON Schema | Chat event contract (13 shapes), generated TypeScript + Python types |
| Cross-module | Make, Git/GitHub | Entry points; monorepo |

Designed, not built yet: Envoy Gateway, Kafka + Spring Kafka, OpenTelemetry / Prometheus / Grafana / Tempo / Loki / Langfuse, Resilience4j, Bucket4j, Presidio, Ragas / DeepEval, k6 / Playwright / axe, Kubernetes (kind) + Helm.

---

## Day 2 notes - Data and infrastructure

### What runs where
- In Docker (Compose, `buywise-deploy/compose/compose.yaml`): postgres (with pgvector), redis, keycloak, litellm, flyway (run once, `tools` profile).
- On the Mac: our 4 apps (services, MCP, agent, Node server) and Ollama (needs the Mac GPU). Apps are not containerised locally so code changes need no image rebuild.
- Containers reach each other by service name (`postgres:5432`), the Mac via `host.docker.internal` (LiteLLM -> Ollama), and the Mac reaches them on `localhost` ports.
- Postgres data lives on the Mac in `PG_DATA_DIR` (`buywise-data/postgres`), so `make down` keeps it. Config files are mounted read-only. Passwords come from `buywise-deploy/compose/.env` (git-ignored).

### Why each piece
| Piece | Kind | Why we use it |
|---|---|---|
| Docker Compose | Tool | One file and one command (`make up`) start and wire the base containers: start order by health check, shared network, settings from `.env`, data kept in a volume. Lighter than Kubernetes locally; production runs the same images on Kubernetes |
| PostgreSQL 17 | Server | One server, a database per deployable (`services`, `agent`, `keycloak`, `litellm`), each with its own user (ADR-010). Transactions, exact money, CHECK rules for business data; jsonb when shape varies; vectors for RAG. AI load cannot slow checkout once split onto two servers in production |
| Schemas in `services` | - | `catalog`, `inventory`, `customers`, `orders` (+ `flyway`). No joins or foreign keys across schemas, so modules stay separable |
| Flyway | Library in the Java app + container | Builds and changes the `services` tables from numbered SQL files in git (V1-V4). Applied files are locked by checksum - change = new file (V3 example). Runs before the seed load (`make migrate`) |
| pgvector | Postgres extension | Meaning search for RAG inside Postgres (ADR-011): bge-m3 1024-number vectors, HNSW index, `<=>` cosine distance. 309 chunks from 92 docs today. No separate vector database at our size |
| Redis | Server | Fast, short-lived data: sessions (TTL), later rate limits and budget counters. Not backed up; losing it is acceptable |
| Redis Streams | Redis feature | `conv:{id}` per conversation: Node server adds the customer message, agent adds reply events, Node server reads with `XREAD BLOCK` and forwards. Kept and replayable (unlike Pub/Sub), ordered, ~1000 events per stream. Kafka stays for business events |
| SSE | Browser standard | Pushes events live to the browser over one HTTP connection; auto-reconnect sends `Last-Event-ID` (= stream entry id) and the Node server replays from there. One-way is all chat needs (vs WebSockets) |
| Keycloak | Server (Java, Docker) | Login with OpenID Connect; our code never handles passwords; identity comes from login, never from the AI (ADR-028). Realm as code. Today the id is passed as `X-Customer-Id` (simplification) |
| LiteLLM | Server (Docker) | Gateway for every model call (ADR-026): our code asks for `buywise-primary` / `buywise-economy` / `bge-m3`, config maps them to Ollama now and a cloud model later. Placeholder prices so spend tracking behaves like production; budgets and fallbacks designed, not built |

### Found on Day 2
- RAG search is vector-only today (no full-text, rerank, filters) and the table is `rag.chunks`, not schema `knowledge` - logged in buywise-docs/09 section 4.
- "BFF" renamed to "Node server" in all docs.

## Progress
- 2026-11-17: Day 1 done. Started the buywise-services technology deep dive (4 parts): part 1 (Java 25 features, Spring container + dependency injection, Spring Boot startup) and part 2 (web layer: request journey, controllers, JSON, validation, errors) done. Resume at part 3 (data layer: HikariCP, JdbcClient, @Transactional, stock reserve, Flyway), then part 4 (Spring Modulith, Gradle, Actuator, tests).
- Gaps found in part 2, logged in buywise-docs/09 section 4 on 2026-11-18: validation 400 does not name the failing field; negative `limit` gives 500 (clamp to 1-20); X-Customer-Id trusted blindly (already a known simplification).
- 2026-11-18: Day 2 part 1 (concepts: why each piece) done - notes above. Resume at Day 2 part 2.1 (`compose.yaml` walkthrough), then 2.2-2.7 and the hands-on; Day 3 parts 3-4 after that.
