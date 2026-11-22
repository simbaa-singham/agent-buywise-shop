# Implementation Roadmap - agent-buywise-shop

Part of [00-architecture-overview.md](00-architecture-overview.md). Status: Approved by architect 2026-10-29. Observability stack stays in phase 7 and prerendered product pages stay in phase 4 (architect decision).

## 1. Approach
- **Priority (architect, 2026-10-30): finish the whole project end to end on the Mac first.** In every phase, build what makes the feature work locally. Deferred until the end: phase 7 (Kubernetes, k6, failure scenarios, observability stack, Lighthouse), phase 8 hardening, and the production extras inside phases 0-6 (CI beyond basic tests, tracing across hops, failure tests like killing the Node server mid-reply, scaling with S and k).
- **Thin vertical slice first:** one real chat turn end to end (browser -> Node server -> agent -> MCP -> services -> back) before widening any layer. Every later phase adds features to a system that already works end to end.
- **Production practices from day one:** contracts, tests, CI, tracing, accessibility checks and PII-safe logging start in phase 0/1, not at the end.
- **Scope rule (buywise-docs/00 section 7.4):** only "implemented locally" items are built; "design only" items stay documented.
- **Before each phase:** recap the listed ADRs and what they mean in code; any new decision is raised to the architect, never made silently.
- **Local usage (buywise-docs/08-buywise-deploy/01-design.md section 4b):** each phase runs only the components it needs.

## 2. Cross-cutting from phase 0 (applies to every phase)
| Practice | Decision |
|---|---|
| Contract-first: JSON Schema in `shared/contracts/`, generated TS + Pydantic, drift check in CI | ADR-024 |
| OpenTelemetry tracing in every deployable; PII masked before logs/traces | ADR-027, ADR-036 |
| Identity never a tool argument; token exchange per hop | ADR-028 |
| Accessibility: angular-eslint a11y rules + axe-core in Playwright | ADR-025 |
| No brand/maker names, no images (placeholders) | ADR-033 |
| Each module has its own tests; CI runs build, unit, contract tests | buywise-docs/08-buywise-deploy/01-design.md section 7 |
| Build tools: Gradle Kotlin DSL + version catalog for Java; uv with committed `uv.lock` for Python | ADR-041, ADR-042 |

## 3. Phases

### Phase 0 - Foundations - DONE 2026-10-29
Verified: stack healthy; 4 isolated databases + pgvector 0.8.7; Flyway V1-V2; seed data (50 products, 240 variants, 10 stores, 2,400 stock rows); Keycloak `buywise` realm; LiteLLM -> Ollama chat + bge-m3 (1024 dims) with shadow cost; k = 2.96 (16.9 tokens/s local vs 50 reference); 6 contract tests + lint green.
| Item | Detail | ADRs |
|---|---|---|
| Local-dev stack (Docker Compose) | Postgres + pgvector (databases per ADR-010), Redis, Keycloak (realm as code), LiteLLM -> Ollama on host | ADR-010, ADR-011, ADR-013, ADR-026 |
| Repo tooling | Makefile (`make up`, `make migrate`, `make ingest`, `make test`), linters/formatters per language, GitHub Actions skeleton | ADR-001 |
| Contracts package | ADR-024 event JSON Schemas + codegen (TS, Pydantic) + CI drift check | ADR-024, ADR-029 |
| ~~Seed data~~ - **done 2026-10-28** (`make data`): full catalog, stores, stock, customers, orders, tickets | ADR-033 |
| Load seed data | One-time manual load by the architect with psql, following buywise-docs/07-buywise-data/03-walkthroughs/01-load-seed-data.md; since 2026-11-18 also `make seed` (ADR-046) | ADR-010, ADR-033 |
| Benchmark `k` | Script measuring local tokens/s; writes `k` to local config | buywise-docs/00 section 7.1 |

**Done when:** `make up && make migrate && make seed` (scripts in buywise-db, ADR-046) gives a running stack with seeded data; CI green on an empty-but-wired repo.

### Phase 1 - Thin slice: "Is the iPhone 18 Pro in stock at my store?" (guest)
| Layer | Build | ADRs |
|---|---|---|
| `buywise-services` | Gradle Kotlin DSL build + version catalog + wrapper; Spring Modulith app; catalog + inventory modules; Flyway; REST + OpenAPI; JWT resource server; Modulith verification test | ADR-014, ADR-010, ADR-041 |
| `buywise-mcp` | `/mcp/catalog`, `/mcp/inventory` servers: `search_products`, `get_product`, `check_stock`; inbound token check, outbound token exchange | ADR-015, ADR-028, ADR-031 |
| `buywise-agent` | FastAPI `POST /turns` (202) + background run; LangGraph: load_context -> route (rules + LLM classifier, phase 1) -> stock_check handler -> respond; events to `conv:{id}` Redis Stream; LLM client via LiteLLM | ADR-008, ADR-026, ADR-029, ADR-030 |
| `buywise-web` Node server | Guest session (Redis), `POST /api/chat/messages` (idempotent), `GET /api/chat/stream` SSE with `Last-Event-ID` replay, token exchange to agent | ADR-004, ADR-020, ADR-021, ADR-024, ADR-029 |
| `customer-web` | Chat widget: CDK-based message list, streaming text, `status.updated`, `block.product_card` (placeholder image); chat SignalStore + SSE adapter | ADR-018, ADR-019, ADR-022, ADR-024, ADR-025 |

**Blocked on architect decision:** Gradle build layout - one build containing services + events vs separate builds sharing the version catalog (ADR-041 open point).

**Done when:** a Playwright test asks a stock question as a guest and gets a streamed, tool-grounded answer; killing the Node server mid-reply and reconnecting completes the reply; contract tests and axe pass; reader-tolerance tests pass (an unknown field and an unknown event type are forwarded by the Node server and ignored by the browser, ADR-044); one trace spans all five hops.

### Phase 2 - Login, identity and customer data
| Item | ADRs |
|---|---|
| Keycloak clients (customer, staff, ops-admin roles), Node server login/logout/callback, session rotation, CSRF, timeout warning | ADR-021, ADR-025 |
| Full token exchange with per-intent scopes and `act` chain; verify Keycloak `act` support | ADR-028 |
| Customer module: profiles, field-level envelope encryption + blind index, OTP (`verify_customer`) with lockout | ADR-036, ADR-032 |
| Guest -> customer conversation linking | buywise-docs/01-buywise-web/01-design.md section 5.1 |

**Done when:** login mid-conversation keeps the chat; a customer can only see their own data (negative tests); OTP brute force is locked out.

### Phase 3 - Knowledge and RAG
| Item | ADRs |
|---|---|
| ~~Knowledge docs in many formats~~ - **done 2026-10-28**: 103 files in 11 formats + eval sets (`buywise-data/knowledge/`, `buywise-data/eval/`) | ADR-033, ADR-039 |
| Ingestion worker: detect -> parser plugins -> Document model -> normalize -> validate -> clean -> chunk -> embed; quarantine; golden tests per format; upload + drop folder | ADR-039 |
| Chunking on the Document model, parent-child, context headers, metadata, embeddings, pgvector + full-text | ADR-011, ADR-034 |
| Embedding bake-off: bge-m3 vs Qwen3-Embedding-0.6B vs nomic-embed-text v1.5 on the RAG eval set (context precision/recall, query latency); winner adopted via blue/green re-index | ADR-040 |
| Retrieval: filters, hybrid search, RRF, rerank, citations; retriever interface | ADR-011 |
| Handlers: product_question, compatibility, store_question, browse/recommend | buywise-docs/03-buywise-agent/01-design.md section 5 |
| Ragas + RAG eval set in CI; "no price from chunks" check | NFR 8 |

**Done when:** every format parses to the expected Document model (golden tests); a corrupted file lands in quarantine with a reason; RAG eval thresholds met (NFR 8); citations point to page / slide / row; zero prices taken from chunks.

### Phase 4 - Ordering
| Item | ADRs |
|---|---|
| Order + payment (mock) modules: cart, checkout with confirmation (MCP `input_required`), payment link, order status, pickup | ADR-014, ADR-015 |
| MCP `/mcp/order`, `/mcp/customer`; per-user rate limits | ADR-031, ADR-032 |
| Product/category pages prerendered; cart, checkout, account client-rendered | ADR-023 |
| Kafka + `buywise-event-publisher` + `buywise-event-consumers`; order/payment/catalog events; idempotent consumers | ADR-009, ADR-016 |

**Blocked on architect decisions:** event schema format (buywise-docs/00 #6), partitions/retention/DLQ (buywise-docs/05-buywise-events/01-design.md), outbox relay vs Debezium (deferred to this phase), RAG re-indexing location (deferred to this phase).

**Done when:** a customer orders through chat with explicit confirmation; order status flows through events; consumers are idempotent under redelivery.

### Phase 5 - Staff console and handoff
| Item | ADRs |
|---|---|
| `staff-console` app: ticket queue (Material table), live updates via SSE composite cursor | ADR-018, ADR-019, ADR-020 |
| Helpdesk module: tickets, assignment, conversation ownership + audit; Node server owner cache | ADR-037 |
| Takeover flow: accept, pause agent, customer <-> staff messages, release/resume | buywise-docs/01-buywise-web/01-design.md section 5.3 |
| Masked contact details with audited reveal; staff MFA | ADR-036, ADR-021 |

**Done when:** a handoff completes end to end in Playwright; customer messages never reach the agent while staff own the chat.

### Phase 6 - LLM operations, budgets and guardrails
| Item | ADRs |
|---|---|
| LiteLLM shadow pricing, global budget; agent per-turn/conversation/customer caps; degradation ladder; admission control queue | ADR-026, buywise-docs/00 section 7.3 |
| `turns`, `llm_calls`, `router_decisions` recording; AI Operations (live summary, explorer, budget view) with ECharts wrapper; dev overlay (`message.metrics`) | ADR-027, ADR-038 |
| Presidio placeholders before every LLM call | ADR-036 |
| Router phase 2: train fast classifier, enable cascade tier 2 | ADR-030 |
| Prompt-injection eval set; agent tool-call caps | NFR 9, ADR-032 |

**Blocked on architect decision:** production LLM (buywise-docs/00 #5) sets the shadow prices and global budget; placeholder prices can be used until then.

**Done when:** budget limits trigger the ladder (never a bare error); AI Operations shows per-stage latency/tokens/cost; injection evals pass.

### Phase 7 - Production-shaped runtime (local-k8s)
| Item | ADRs |
|---|---|
| Helm chart per deployable; `values-local.yaml` filled from `buywise-deploy/local/scale.yaml` (`S`, `k`; ADR-045); kind cluster; Envoy Gateway (TLS, routing, rate limits) | ADR-013, ADR-017, buywise-docs/08-buywise-deploy/01-design.md |
| Observability stack: OTel Collector (redaction processor), Prometheus, Grafana (SLO + budget alerts), Tempo, Loki | ADR-027, ADR-036 |
| Probes, limits, graceful shutdown, PDBs, rolling deploys, HPA 2 -> 3 | buywise-docs/08-buywise-deploy/01-design.md section 6 |
| Failure scenarios (buywise-docs/00 section 7.2 #6) and k6 at local scale, incl. LLM capacity test (replies generating at once before each drops below 50/k tokens/s; sets the admission limit) | NFR 1, 5, 6, 7, ADR-045 |
| Lighthouse CI (Core Web Vitals) | NFR 3 |

**Done when:** all local NFR targets in buywise-docs/00 section 7.2 are met and reported on Grafana.

### Phase 8 - Data lifecycle and hardening
| Item | ADRs |
|---|---|
| Retention jobs (transcripts 90 d, logs 30 d, traces 14 d) | NFR 11, ADR-036 |
| Privacy export/deletion jobs from the staff console, audited | ADR-036 |
| Full accessibility manual checklist pass | ADR-025 |
| Review design-only items (buywise-docs/00 section 7.4) against what was built | - |

## 4. Open decisions by phase
| Decision | Needed by |
|---|---|
| Gradle build layout: one build (services + events) vs separate builds sharing the catalog (ADR-041) | Phase 1 |
| Make generated knowledge documents byte-deterministic (fixed MIME boundaries, timestamps, document IDs) so `make data` gives no diff - needed for stable golden tests | Phase 3 |
| Order status updates for orders without a conversation (placed on the website): `order.status_changed` requires `conversationId` today - where do they go (customer stream, notification only, optional field)? | Phase 4 |
| Event schema format (buywise-docs/00 #6) | Phase 4 |
| Partitions, retention, dead-letter topics (buywise-docs/05-buywise-events/01-design.md) | Phase 4 |
| Outbox relay vs Debezium (deferred) | Phase 4 |
| RAG re-indexing location (deferred) | Phase 4 |
| Ticket categories as a fixed list (`ticket.*` `category` is free text in the chat contract) | Phase 5 |
| Production LLM (buywise-docs/00 #5) | Phase 6 (placeholder prices until then) |
| Secrets management (buywise-docs/08-buywise-deploy/01-design.md) | Production design only; local uses Kubernetes secrets |

## 4. Local end-to-end build (2026-10-30) - simplifications to revisit
Built in one pass to get the whole core assistant running on the Mac (architect priority). What differs from the decided design:

| Area | Decided | Built locally now | Revisit when |
|---|---|---|---|
| Identity between hops | Token exchange per hop (ADR-028) | Node server puts the logged-in customer id in the agent request; agent sends it to MCP as `X-Customer-Id`; MCP to services the same. Never a tool argument. No JWT checks on agent/MCP/services. | Production hardening |
| Intent routing | Rules -> classifier -> LLM cascade (ADR-030) | The model picks tools itself (one LLM loop) | Router eval work |
| Order confirmation | Explicit confirmation | `place_order` becomes a quote; the order is placed only on the customer's "yes" (deterministic, not by the model) | - (keep) |
| Document parsing | Plugin pipeline, 11 formats (ADR-039) | md, txt, html, digital pdf, docx; staff-only / superseded / not-yet-effective docs skipped | Phase 3 |
| Customer lookup at login | Customer id claim in token | Customer found by the verified email from Keycloak | Phase 2 |
| Session cookie | `__Host-` cookie, idle timeout (ADR-021) | `bw_sid` HttpOnly SameSite=Lax, 8 h | Production hardening |
| Chat UI state | SignalStore (ADR-022) | SignalStore fed only by the SSE stream; replay rebuilds history | - |
| Metrics, budgets, tracing | ADR-026/027 | Not built (no `message.metrics`, no budget ladder, no OTel) | Phase 6 / 7 |
| Staff console, handoff, Kafka events | Phases 4-5 | Not built | Next phases |
| Versions | NestJS 11 | NestJS 12 (current), TypeScript 7 in the Node server | - |
| RAG search | Hybrid: pgvector + full-text, RRF, rerank, filters (ADR-011); schema `knowledge` in `agent` (ADR-010) | Vector-only (cosine, HNSW, top 5); table `rag.chunks` | Phase 3 |
| Services request checks | Clear 4xx for bad input | Validation 400 does not name the failing field; negative `limit` gives 500 (should clamp to 1-20) | Phase 1 |

## 5. To-do list - fix later
Small fixes found during the deep dive. Tick when done.

- [ ] **Keycloak: dev mode -> production mode** (found 2026-11-22). Today `compose.yaml` runs `kc.sh start-dev --import-realm` (plain HTTP, relaxed hostname checks, less caching). Production mode: `kc.sh start --optimized` on an image pre-built with `kc.sh build` (database type, health set at build time); HTTPS with a certificate (or plain HTTP only behind Envoy with `--proxy-headers=xforwarded`); fixed `--hostname`; realm applied on every deploy (keycloak-config-cli) instead of a one-time `--import-realm`. Files: `buywise-deploy/compose/compose.yaml`, `buywise-deploy/compose/keycloak/`, Helm values later. When: production hardening (phase 7).
- [ ] **Demo user has no `customer` role** (found 2026-11-22). `add-demo-user.sh` creates `demo` with only `default-roles-buywise`. Add `kcadm.sh add-roles -r buywise --uusername demo --rolename customer` to the script (or make `customer` part of the realm's default roles in `buywise-realm.json`). Matters once services/agent check roles. When: phase 2.
- [ ] **Node server fallback client secret** (found 2026-11-22). `buywise-web/server/src/config.ts` falls back to a hard-coded `OIDC_CLIENT_SECRET`; if it differs from `CUSTOMER_WEB_CLIENT_SECRET` in `compose/.env`, login fails with "Login failed (401)". Remove the fallback and fail at startup when the secret is missing. When: phase 2.
- [ ] **Feature: customer sign-up with Google or a sign-up form** (requested 2026-11-22, ADR-049). Keycloak-hosted register form + Google identity provider; email verification for form sign-ups (Mailpit container locally); Node server callback creates the `customers` row on first login (needs new services `POST /api/customers`); new users get the `customer` role; same-email accounts linked only after proof of ownership. Needs a Google Cloud OAuth client (architect). When: after the deep-dive week (next-feature pick).
- [ ] **Redis keeps data although compose says "no volume"** (found 2026-11-22). The redis image declares `/data` as a volume, so Docker creates an anonymous volume and Redis saves snapshots (`save 3600 1 300 100 60 10000`); streams from 2026-10-30 are still there. Decide: make it truly short-lived (`command: redis-server --save "" --appendonly no`) or keep persistence on purpose and fix the comment (ADR-035). When: phase 2.
- [ ] **Conversation streams never expire** (found 2026-11-22). `conv:{id}` streams have no TTL (`ttl = -1`); only the length is capped. Set an expiry (e.g. refreshed on each write) so old conversations leave Redis. When: phase 2.
- [ ] **Embedding calls show 0 tokens / $0 in LiteLLM spend** (found 2026-11-22). `bge-m3` rows in `LiteLLM_SpendLogs` have 0 prompt tokens, so RAG cost is not counted (ADR-026). Check whether Ollama returns token counts for embeddings or count them in the agent. When: phase 6.
- [ ] **Learning: Redis design walkthrough** (added 2026-11-22, architect). At the end of the deep-dive week, go through the whole Redis design: what is stored (sessions, conversation streams; planned rate limits and budget counters), key names and expiry, stream length cap, persistence choice (ADR-035), Streams vs Pub/Sub vs Kafka (ADR-029), how replay with `Last-Event-ID` works, and the production setup (high availability, memory limits). Docs: buywise-docs/00, buywise-docs/08-buywise-deploy/01-design.md, ADR-021/026/029/032/035. When: after day 7.
