# agent-buywise-shop - Architecture Overview

An AI shopping assistant that helps customers choose, order and track electronic devices.

Main design document. Module-level detail lives in the linked module docs (01-08).
Decisions are recorded in [adr/ADR_Log.md](adr/ADR_Log.md).

| Field | Value |
|---|---|
| Owner / Architect | Sachin Wakade |
| Purpose | Learning and portfolio project: production-grade design and code, run locally at small scale |
| Status | Draft - under review |
| Last updated | 2026-10-28 |

## 1. Purpose and scope

AI shopping assistant for an online electronics store (Apple products as the sample catalog, US). It helps customers:
1. Choose a device (discover, compare, configure).
2. Place an order (stock check, cart, checkout; delivery or in-store pickup).
3. Track an order (delivery tracking or pickup readiness).
4. Get answers to product and store questions, and reach store staff when needed.

**Out of scope (v1):** returns, exchanges, refunds, trade-ins, voice channel, real payment processing (mock payment links only).

**Runtime:** not hosted. Runs on a Mac with production-shaped infrastructure at small scale; production sizing is configuration only.

## 2. Key decisions (summary)

| Area | Decision | ADR |
|---|---|---|
| Repository | One monorepo with modules | ADR-001 |
| Language split | Java for business services; Python for AI and MCP; TypeScript for UI/BFF | ADR-002 |
| UI | Angular 22 | ADR-003 |
| BFF | Node.js 24 LTS, NestJS 11 + Fastify; serves the Angular build | ADR-004 |
| Business services | One Spring Boot 4.1 modular monolith (Spring Modulith) | ADR-014 |
| MCP | Separate `buywise-mcp` deployable, MCP Python SDK v2, spec 2026-07-28 | ADR-015 |
| Deployables | 6 deployables (see section 5) | ADR-016 |
| Edge | Envoy Gateway (Kubernetes Gateway API); no internal gateway; service mesh as future option | ADR-017 |
| Agent orchestration | LangGraph 1.2 with Postgres checkpointer | ADR-008 |
| Events | Apache Kafka; separate publisher and consumer deployables | ADR-009 |
| Primary database | PostgreSQL, schema per module | ADR-010 (proposed) |
| Vector store | Postgres + pgvector + full-text (hybrid) | ADR-011 (proposed) |
| Runtime | Local-first, small scale; production sizing via config only | ADR-013 |

## 3. System context

| Actor / system | Interaction |
|---|---|
| Customer | Website chat: browse, order, track, questions |
| Store staff | Staff console: tickets, take over conversations |
| Identity provider (Keycloak) | Customer and staff login, service tokens, MCP authorization |
| Payment provider (mock) | Payment links and payment status callbacks |
| Shipping carrier (mock) | Tracking numbers and delivery events |
| LLM provider | Always via the model gateway (LiteLLM proxy, ADR-026): Ollama on the Mac locally; vLLM or hosted API in production design. Shadow pricing applied locally |

## 4. High-level architecture

**Layers**
1. **Edge** - Envoy Gateway: TLS, routing, rate limits for browser traffic.
2. **Experience** - `buywise-web`: Angular 22 app + NestJS BFF (session, SSE streaming, screen aggregation).
3. **AI** - `buywise-agent`: LangGraph agent + RAG pipeline.
4. **Tools** - `buywise-mcp`: MCP servers wrapping the business REST APIs.
5. **Business** - `buywise-services`: Spring Boot modular monolith (catalog, inventory, order, customer, payment mock, helpdesk).
6. **Events** - `buywise-event-publisher` and `buywise-event-consumers` with Kafka.
7. **Data and platform** - Postgres, Redis, Kafka, Keycloak, LiteLLM model gateway, observability, Kubernetes.

**Request path (chat message)**
1. Browser -> Envoy Gateway -> `buywise-web` (HTTP POST to send; SSE stream to receive).
2. BFF -> `buywise-agent` (streaming HTTP).
3. Agent: load state -> sentiment -> intent router -> intent handler.
4. Handler -> `buywise-mcp` (MCP, stateless) -> `buywise-services` REST.
5. Handler -> RAG retrieval for knowledge questions.
6. Agent -> guardrails -> streamed response -> BFF -> browser.

**Screen path (e.g. order history)**
1. Browser -> `buywise-web` BFF -> `buywise-services` REST (JWT from the session).

**Event path**
1. `buywise-services` commits state + event record in one DB transaction.
2. `buywise-event-publisher` publishes committed events to Kafka (mechanism deferred, see section 8).
3. `buywise-event-consumers` react: notifications, staff console updates, projections.
4. RAG re-indexing on catalog changes (location deferred, see section 8).

## 5. Deployables and modules

| # | Deployable | Contains | Stack | Detailed design |
|---|---|---|---|---|
| 1 | `buywise-web` | Angular app + NestJS BFF (BFF serves the Angular build) | Angular 22, Node.js 24, NestJS 11 + Fastify | [01](01_UI_Angular_BFF_Design.md) |
| 2 | `buywise-services` | Modular monolith: catalog, inventory, order, customer, payment (mock), helpdesk | Java 25, Spring Boot 4.1, Spring Modulith | [02](02_Services_SpringBoot_Design.md) |
| 3 | `buywise-agent` | LangGraph agent, RAG pipeline, evals | Python 3.12, LangGraph 1.2 | [03](03_Agent_Python_Design.md), [04](04_RAG_Design.md) |
| 4 | `buywise-mcp` | MCP servers wrapping `buywise-services` REST APIs | Python 3.12, MCP Python SDK v2 (spec 2026-07-28) | [05](05_MCP_Design.md) |
| 5 | `buywise-event-publisher` | Kafka producers for committed business events | Java (Spring Kafka) - design deferred | [06](06_Eventing_Kafka_Design.md) |
| 6 | `buywise-event-consumers` | Kafka consumers for async reactions | Java (Spring Kafka) - design deferred | [06](06_Eventing_Kafka_Design.md) |

Data stores are covered in [07](07_Data_Database_Design.md); environments and deployment in [08](08_Deployment_Design.md).

## 6. Repository layout

```
agent-buywise-shop/
├── ui/                  # buywise-web: Angular 22 app + NestJS BFF
│   ├── web/             # Angular workspace (customer-web, staff-console, shared)
│   └── bff/             # NestJS 11 + Fastify
├── services/            # buywise-services: one Spring Boot app (modules as packages)
├── mcp/                 # buywise-mcp: Python MCP servers
├── agent/               # buywise-agent: LangGraph agent, RAG, evals
├── events/
│   ├── publisher/       # buywise-event-publisher
│   └── consumers/       # buywise-event-consumers
├── data/                # local infra (Postgres, Redis, Kafka, Keycloak), seed data, knowledge docs
├── deploy/              # Docker Compose, Helm charts, GitHub Actions
└── docs/
```

## 7. Non-functional requirements

Production targets are ideal production-grade targets (SLOs with error budgets). Local targets are the same system scaled down proportionally, and every limit has defined behavior when exceeded (section 7.3). The LLM is treated as a paid production service everywhere, including locally (shadow pricing, ADR-026).

### 7.1 Scaling rules (production -> local)
| Kind of target | Rule | Value |
|---|---|---|
| Volume (users, chats, requests/s, concurrency) | Divide by scale factor `S` | `S = 40` |
| Non-LLM latency (pages, REST, MCP tools, first visible feedback, system overhead) | Same as production - same code, small data | x1 |
| LLM-dependent latency and speed (TTFT model part, full answer, tokens/s) | Multiply (or divide speed) by hardware factor `k` | `k` = production model tokens/s / local model tokens/s, measured by a benchmark at setup |
| Error rates, correctness, security, accessibility, retention | Same as production | x1 |
| Availability | Proven by failure scenarios instead of uptime over months | see 7.2 #6 |

`S` and `k` live in `values-local.yaml` (docs/08); every derived local limit (concurrency caps, rate limits, LLM timeouts) is computed from them, never hand-tuned.

### 7.2 Targets
| # | Category | Production target | Local target (S = 40, k measured) |
|---|---|---|---|
| 1 | Scale | 200k customers; 50k chats/day; 2,000 concurrent chats (~300 generating at once); 100 chat msgs/s; 1,000 API req/s steady | 5k customers; 1,250 chats/day; 50 concurrent chats (~8 generating); 2.5 msgs/s; 25 req/s (k6) |
| 2 | Spikes | 10x browsing, 3x chats absorbed by autoscaling; beyond that admission control (7.3) | Same multipliers on local base: 250 req/s browsing, 150 concurrent chats; beyond LLM capacity -> queue |
| 3 | Web performance | Core Web Vitals p75: LCP < 2.5 s, INP < 200 ms, CLS < 0.1 | Same (Lighthouse CI on prerendered and client routes) |
| 4 | API latency | BFF and services REST p95 < 200 ms, p99 < 500 ms; MCP tool call p95 < 200 ms, p99 < 500 ms | Same |
| 5 | Chat latency | First visible feedback (`status.updated`) p95 < 500 ms. First reply token p95 < 1 s (no tool) / < 2 s (tool turns), p99 < 3 s. Full answer p95 < 5 s. Output >= 50 tokens/s per stream. System overhead (everything except model inference) <= 300 ms no-tool / 800 ms tool turns | First visible feedback and system overhead: same as production. Model-dependent parts: production target x k; output >= 50/k tokens/s |
| 6 | Availability | Chat 99.95% (~22 min/month); checkout 99.99% (~4 min/month); multi-zone | Zero failed requests in each failure scenario: kill any pod of a 2-replica deployable; kill BFF pod mid-reply (reply completes after reconnect); restart Redis; stop LiteLLM; stop Ollama; Postgres failover (when the resilience profile runs 2 Postgres instances, docs/08 open decision 2) |
| 7 | Error rate | Server errors < 0.1% of requests; chat turns with neither an answer nor a fallback < 0.1% | Same, during the k6 run |
| 8 | Correctness | Intent routing accuracy >= 95%; prices/stock/status not from a tool result = 0; knowledge answers with a citation >= 95% | Same (scenario eval suite in CI) |
| 9 | Security | OAuth2/JWT; least-privilege tools; PII masked; no card data in any system (PCI DSS out of scope, mock payment links); ADR-021 session rules; prompt-injection test set in evals | Same |
| 10 | Data recovery | Orders: RPO 0 (synchronous replica), RTO 15 min. Other data: RPO 5 min, RTO 1 h | One tested point-in-time restore (backup + WAL replay) measured against the same RPO/RTO |
| 11 | Data retention | Chat transcripts (incl. `turns`, `llm_calls`) 90 days, then deleted or anonymized; logs PII-masked, 30 days | Same, as scheduled jobs |
| 12 | Accessibility | WCAG 2.2 AA (ADR-025) | Same |
| 13 | LLM cost | Enforced budgets (ADR-026): per-turn output cap, per-conversation cap (20k tokens), per-customer daily cap, global daily USD budget (alert 80%, cheaper model 90%, stop 100%) | Same caps; global daily USD budget / S; shadow pricing on Ollama |

### 7.3 Behavior when limits are exceeded or dependencies fail
Same mechanisms locally and in production; only the limits differ (derived from `S` and `k`).

| Situation | Mechanism | User sees |
|---|---|---|
| Browsing/API traffic above capacity | Envoy rate limits (per IP, per session); load shedding with `503` + `Retry-After` on non-critical APIs; checkout traffic prioritized | Retry with backoff in the UI; checkout unaffected |
| Too many chats generating at once | Admission control in the agent: concurrency cap per pod; excess turns queued (bounded queue, max wait) | `status.updated` "You're next..." with position; if max wait exceeded -> FAQ answers + staff handoff offer |
| Slow LLM | Per-stage deadlines (whole turn 15 s x k; LLM call 10 s x k; tool call 2 s); stream keeps `status.updated` flowing | Progress messages; on deadline -> fallback model, then FAQ + handoff |
| LLM/LiteLLM down | Circuit breaker (open at 50% failures over 20 calls, half-open after 30 s) | FAQ answers from RAG retrieval (no generation) + staff handoff |
| Tool/service errors | Retries only for idempotent calls (2, exponential backoff + jitter); circuit breakers (Resilience4j in services, policies in LangGraph nodes) | "I couldn't check stock right now" + retry or handoff; never invented data |
| Budget limits hit | Degradation ladder (ADR-026, docs/03 section 7a) | Cheaper model, then FAQ + handoff; per-turn cap -> "Want me to continue?" |
| SSE stream drops | Auto-reconnect + `Last-Event-ID` replay (ADR-020/024); REST reload if gap too old | Reply continues where it stopped |
| Redis down | Sessions unavailable -> login prompt; replay/budget counters fail closed for budgets, open for replay (REST reload) | Re-login; chat history reloads |
| Duplicate sends (retries) | `clientMessageId` idempotency (ADR-024) | Message appears once |

## 8. Cross-cutting concerns

- **Security:** Keycloak for customers, staff and service accounts; BFF session pattern; Spring Security JWT checks in `buywise-services`; OAuth for `buywise-mcp`; OTP for order status. Service mesh (mTLS) is the future path for service-to-service security.
- **Observability:** OpenTelemetry end to end (browser -> BFF -> agent -> MCP -> services); Langfuse for LLM traces; Prometheus/Grafana; structured logs. LLM latency, speed, tokens and cost per call (OTel GenAI conventions) on Grafana and in the staff-console AI Operations area (ADR-027).
- **Resilience:** timeouts, retries, circuit breakers (Resilience4j, LangGraph node policies); fallback to human handoff.
- **Evaluation:** RAG and agent scenario suites in CI (Ragas, DeepEval); contract tests for MCP tools and REST APIs.
- **Governance:** versioned tool schemas and APIs; ADRs for every major decision.

## 9. Open and deferred decisions

| # | Decision | Status |
|---|---|---|
| 1 | Confirm NFR targets (section 7) | Decided 2026-10-28 |
| 2 | Event publishing mechanism: polling outbox relay vs Debezium CDC | Deferred to implementation |
| 3 | Where RAG re-indexing runs: agent vs event consumers | Deferred to implementation |
| 4 | Vector store: pgvector (proposed) vs Qdrant | Open |
| 5 | Production LLM: self-hosted (vLLM) vs hosted API behind a gateway | Open |
| 6 | Event schema format: JSON Schema vs Avro (+ schema registry) | Open |
| 7 | Angular component library | Decided (ADR-019) |
