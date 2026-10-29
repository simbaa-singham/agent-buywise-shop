# Architecture Decision Log - agent-buywise-shop

| ADR | Decision | Status | Date |
|---|---|---|---|
| ADR-001 | One monorepo with modules | Accepted | 2026-10-28 |
| ADR-002 | Java for business services, Python for AI and MCP, TypeScript for UI/BFF | Accepted | 2026-10-28 |
| ADR-003 | Angular 22 for the web UI (chosen over 21: stable signal APIs, longer support) | Accepted | 2026-10-28 |
| ADR-004 | NestJS 11 + Fastify BFF on Node.js 24 LTS; serves the Angular build (one deployable) | Accepted | 2026-10-28 |
| ADR-005 | Spring Cloud Gateway as internal gateway | Superseded by ADR-017 | 2026-10-28 |
| ADR-006 | Java 25 + Spring Boot 4.1 as six microservices | Superseded by ADR-014 | 2026-10-28 |
| ADR-007 | MCP servers inside Java services (Spring AI 2.0) | Superseded by ADR-015 | 2026-10-28 |
| ADR-008 | LangGraph 1.2 for agent orchestration with Postgres checkpointer | Accepted | 2026-10-28 |
| ADR-009 | Kafka for events; events recorded in the same transaction as state changes | Accepted (mechanism deferred) | 2026-10-28 |
| ADR-010 | PostgreSQL: database per deployable (services with schema per module, agent, keycloak, litellm, langfuse); production business and AI clusters; one cluster locally | Accepted | 2026-10-28 |
| ADR-011 | Postgres + pgvector + full-text for RAG (hybrid, RRF, rerank); retriever interface; `pg_search` BM25 upgrade path; RAG reads off the primary in production | Accepted | 2026-10-28 |
| ADR-012 | Project name agent-buywise-shop; electronics shopping assistant; catalog of real products (model names, specs, list prices), maker never named, more makers later (amended 2026-10-28, see ADR-033) | Accepted | 2026-10-28 |
| ADR-013 | Local-first, small-scale runtime; production sizing via configuration only | Accepted | 2026-10-28 |
| ADR-014 | One Spring Boot 4.1 modular monolith (Spring Modulith 2.x), controllers per use case | Accepted | 2026-10-28 |
| ADR-015 | `buywise-mcp` as separate deployable, MCP Python SDK v2, spec 2026-07-28, wrapping REST APIs | Accepted | 2026-10-28 |
| ADR-016 | Six deployables: web, services, agent, mcp, event-publisher, event-consumers | Accepted | 2026-10-28 |
| ADR-017 | Envoy Gateway at the edge; no internal gateway; Spring Security in services; service mesh as future option | Accepted | 2026-10-28 |
| ADR-018 | UI app structure: one Angular workspace with two apps (customer-web, staff-console) + shared library; one deployable | Accepted | 2026-10-28 |
| ADR-019 | Angular Material (Material 3) + CDK with custom theme; SCSS + design tokens, no Tailwind; custom chat UI on CDK | Accepted | 2026-10-28 |
| ADR-020 | Browser real-time channel: SSE (server -> browser) + HTTP POST (browser -> server); Redis pub/sub across pods (amended by ADR-029: Redis Streams), no sticky sessions; WebSocket as planned upgrade for staff takeover | Accepted | 2026-10-28 |
| ADR-021 | Session pattern: BFF session (token handler), tokens in Redis, opaque `__Host-` cookie; guest sessions; separate staff session with MFA | Accepted | 2026-10-28 |
| ADR-022 | UI state: NgRx SignalStore for shared/live state, plain signals for local state, `httpResource` for read-only server data | Accepted | 2026-10-28 |
| ADR-023 | UI rendering: hybrid per route - prerender product/category pages, client rendering elsewhere; no per-request SSR | Accepted | 2026-10-28 |
| ADR-024 | Chat message contract: own versioned JSON Schema envelope, AG-UI-shaped reply events, structured blocks, Redis Stream replay (amended by ADR-029: SSE id = stream entry id, `seq` removed), idempotent sends | Accepted | 2026-10-28 |
| ADR-025 | Accessibility: WCAG 2.2 AA enforced by angular-eslint + axe-core in CI plus a manual per-release checklist; chat-specific rules | Accepted | 2026-10-28 |
| ADR-026 | LLM metering and budgets: LiteLLM model gateway (pricing, spend, global budget, rate limits) + agent LLM client (per-turn/conversation/customer caps, degradation); shadow pricing locally | Accepted | 2026-10-28 |
| ADR-027 | LLM observability in the UI: Grafana for trends/alerts + staff-console AI Operations (ops-admin) + customer-web dev overlay; `status.updated` and `message.metrics` events | Accepted | 2026-10-28 |
| ADR-028 | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop BFF -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-lived JWTs with `act` chain; identity never a tool argument | Accepted | 2026-10-28 |
| ADR-029 | Agent output path: background turns (`POST /turns` 202); agent appends ADR-024 events to per-conversation Redis Stream; BFF pods read and forward; replaces pub/sub and separate replay buffer | Accepted | 2026-10-28 |
| ADR-030 | Intent routing: cascade of rules -> fast in-process classifier -> economy-tier LLM classifier; clarify then handoff on low confidence; flow stickiness; decisions logged | Accepted | 2026-10-28 |
| ADR-031 | MCP layout: one server per domain (`/mcp/{domain}`) in one process and image; agent connects per intent; optional per-domain Deployment in production | Accepted | 2026-10-28 |
| ADR-032 | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j | Accepted | 2026-10-28 |
| ADR-033 | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs, Faker customers/orders, fixed seeds, no images | Accepted | 2026-10-28 |
| ADR-034 | RAG chunking: structure-aware per doc type, parent-child retrieval, context headers, metadata filters; sizes tuned with Ragas | Accepted | 2026-10-28 |
| ADR-035 | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; Redis/Kafka not backed up; config in Git; no local backups | Accepted | 2026-10-28 |
| ADR-036 | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; masked logs/traces; audited staff reveal; retention and privacy-rights jobs | Accepted | 2026-10-28 |
| ADR-037 | Conversation ownership owned by the helpdesk module in `buywise-services`; BFF caches in Redis; agent paused/resumed as second check | Accepted | 2026-10-28 |
| ADR-038 | AI Operations charts: Apache ECharts (modular imports) with own thin signal-based wrapper; "view as table" accessibility toggle | Accepted | 2026-10-28 |

## Deferred decisions
| Topic | Options | Decide at |
|---|---|---|
| Event publishing mechanism | Polling outbox relay vs Debezium CDC | Implementation of events |
| RAG re-indexing location | Agent vs event consumers | Implementation of RAG |
| Production LLM | A. Hosted frontier API; B. Self-hosted open-weight on vLLM; C. Hybrid tiers via LiteLLM (primary frontier, economy tier for routing/FAQ/fallback, second provider failover, vLLM later). Rough cost: ~400k turns/day x ~4k in / 300 out tokens -> ~$6,600/day at $3/$15 per 1M before caching and tiering. Model picked by eval suite through LiteLLM. Sets shadow prices, `k` and the global budget | Architect to decide later |
| Event schema format | A. JSON Schema, no registry (CI contract tests only); B. Avro + registry (strongest runtime compatibility checks, mature Java/Python, fits Debezium); C. Protobuf + registry (strong codegen, field-number rules); D. JSON Schema + registry (readable, less mature compatibility checks). Related: compatibility mode (e.g. backward transitive), CloudEvents headers, registry choice (Apicurio vs Karapace) and its local footprint | Architect to decide later |

## Template (one section per ADR when detailed)
- **Context:** what problem / forces.
- **Options considered:** with pros and cons.
- **Decision:** what we chose.
- **Consequences:** trade-offs, risks, follow-ups.

## ADR-018 - UI app structure
- **Context:** Two audiences (customers, store staff) with different features and security needs, served by one `buywise-web` deployable.
- **Options considered:**
  - A. One app, lazy-loaded `/staff` area behind a role guard - simplest, but one Keycloak client and staff code exposed on the public site.
  - B. Two apps in one workspace + shared library - separate Keycloak clients and bundles; two build configs.
  - C. Micro-frontends - independent releases, but heavy complexity for one team and one deployable.
- **Decision:** B. `customer-web` at `/`, `staff-console` at `/staff`, `shared` library for common chat/model/API code.
- **Consequences:** Separate Keycloak clients allow stricter staff login; Envoy can restrict `/staff/**`. Two builds to maintain; `shared` must contain only genuinely common code, and apps must not import from each other (enforce with lint rules).

## ADR-019 - UI component library
- **Context:** customer-web needs a branded store look and a custom chat UI; staff-console needs data-heavy screens; both must meet WCAG 2.2 AA.
- **Options considered:**
  - A. Angular Material (M3) + CDK - official, released with Angular, strong accessibility, data table; default look is Google Material.
  - B. Headless (CDK + Angular Aria) + own styling - full visual control; most styling work, no ready data table, Angular Aria maturity to verify.
  - C. PrimeNG - richest component set; third-party release lag, uneven accessibility, some paid extras.
  - D. Spartan (shadcn-style) - copy-in components, full control; younger project, we own maintenance.
- **Decision:** A. Material directly in staff-console; custom M3 theme for customer-web; chat UI custom-built in `shared` on CDK primitives. SCSS with Material design tokens; no Tailwind.
- **Consequences:** Low upgrade effort and good accessibility baseline. Effort needed to make customer-web not look like default Material. Custom chat components need their own accessibility testing.

## ADR-020 - Browser real-time channel
- **Context:** Browser needs streamed agent replies, live staff-takeover messages, ticket queue updates and order status pushes. Traffic is mostly server -> browser; customers send occasional messages. Two BFF pods behind Envoy.
- **Options considered:**
  - A. WebSocket - one bidirectional channel, best for high-frequency two-way traffic; custom heartbeat/reconnect/replay, sticky sessions in the draft.
  - B. SSE + HTTP POST - plain HTTP, built-in reconnect with `Last-Event-ID` replay, same pattern as LLM APIs (OpenAI, Anthropic, Gemini); one-way, so sends are POSTs.
  - C. Socket.IO - rooms, acks, Redis adapter; proprietary protocol on both ends, harder to observe.
  - D. Long polling - legacy, poor streaming.
- **Decision:** B. `GET /api/chat/stream` (SSE) for all server -> browser events; `POST /api/chat/messages` for sends. Redis pub/sub routes events to the pod holding the stream. No sticky sessions.
- **Consequences:** Simple load balancing and standard HTTP tooling. Need event ids and a short-lived replay buffer per stream. Frequent two-way signals (typing, read receipts) would be many small POSTs.
- **Planned upgrade:** If staff takeover needs typing indicators or read receipts, add WebSocket for the staff takeover conversation only. AI streaming stays on SSE. Common production pattern: SSE for AI streaming, WebSocket for human-to-human chat.

## ADR-021 - Session pattern
- **Context:** Browser must stay logged in with Keycloak; tokens must be protected from XSS; SSE (`EventSource`) cannot set auth headers; customers can shop as guests; staff need stricter controls.
- **Options considered:**
  - A. BFF session / token handler - tokens server-side in Redis, opaque httpOnly cookie; recommended by IETF "OAuth 2.0 for Browser-Based Applications"; needs session store and CSRF protection.
  - B. Tokens in the Angular app (public client) - no server sessions; tokens exposed to XSS, refresh token in browser, awkward with SSE.
  - C. Encrypted tokens in the cookie - no store; 4 KB cookie limit, hard server-side revocation.
- **Decision:** A. Authorization Code + PKCE in the BFF; Redis session store; `__Host-` `HttpOnly` `Secure` `SameSite=Lax` cookie; guest sessions upgraded on login with session id rotation; separate staff client and cookie scoped to `/staff`, `/api/staff`, shorter idle timeout, MFA; CSRF via SameSite + custom header.
- **Consequences:** Tokens never reach the browser; SSE works with the cookie. BFF owns refresh and logout. Redis becomes critical for login state (already used for pub/sub). Identity propagation to agent/MCP is an open item in docs/03 and docs/05.

## ADR-022 - UI state management
- **Context:** Angular 22 is signal-first. State includes a live chat conversation (shared by both apps), session, cart, a live staff ticket queue, and read-only page data.
- **Options considered:**
  - A. Plain signals in services - no library; no enforced structure, own entity helpers, no standard devtools.
  - B. NgRx SignalStore - signal-based, consistent composable stores, `withEntities`, stream helpers; one more library.
  - C. Classic NgRx Store (Redux) - excellent devtools and time travel; heavy boilerplate, RxJS-centric, overkill here.
- **Decision:** B, with rules: plain signals for component-local state; `httpResource` for read-only server data; SignalStore for shared or SSE-updated state (chat, session, cart, ticket queue).
- **Consequences:** Predictable, testable stores where complexity lives; simple screens stay simple. Team must learn SignalStore. One SSE-to-store adapter in `shared`. Confirm `httpResource` stability in Angular 22 before coding.

## ADR-023 - UI rendering
- **Context:** Product/category pages benefit from fast first load and SEO; chat, cart, checkout and account are personal and use browser-only SSE; staff-console is behind login. Small, mostly static sample catalog.
- **Options considered:**
  - A. CSR everywhere - simplest; slower first load, weak SEO and link previews.
  - B. SSR for customer-web - fast and indexable everywhere; BFF renders every request, all shared code must be server-safe, no gain on personal pages.
  - C. Hybrid per route - prerender product/category pages, client rendering for the rest.
- **Decision:** C. Angular per-route render modes: Prerender for product/category, Client for chat/cart/checkout/account and all of staff-console. No per-request SSR.
- **Consequences:** BFF stays a file server; prerendered output suits the future CDN option. Price/stock must be fetched live on product pages. Catalog content changes need a rebuild. Prerendered code must guard browser-only APIs. Upgrade path: Server render mode for product routes.

## ADR-024 - Chat message contract
- **Context:** The SSE stream and message POSTs are the central UI interface, used by the agent, BFF and both apps. It carries agent and non-agent events (staff messages, tickets, order status).
- **Options considered:**
  - A. Own typed contract - covers all event kinds, explicit versioning; we maintain it.
  - B. AG-UI protocol - published standard with TS/Python SDKs; agent events only, community Angular support, still evolving.
  - C. Forward raw LangGraph events - no mapping; leaks internals, UI breaks on graph refactors.
- **Decision:** A, with agent-reply events shaped like AG-UI start/content/end. Versioned envelope (`v`, `seq`, `ts`, `conversationId`, `messageId`, `payload`); structured `block.*` content rendered by components; sanitized Markdown for text; Redis Stream replay keyed by `seq`/`Last-Event-ID`; `clientMessageId` for idempotent sends; JSON Schema in `shared/contracts/` generating TS and Pydantic types, drift checked in CI.
- **Consequences:** One contract across Python and TypeScript; adoption of AG-UI remains possible. We own schema evolution. Open item in docs/03: whether the agent emits contract events directly or the BFF maps them.

## ADR-025 - Accessibility
- **Context:** US online store (WCAG 2.x AA is the de facto ADA benchmark). Custom chat UI with streaming text, overlays, OTP and session timeouts.
- **Options considered:**
  - A. WCAG 2.2 AA, automated + manual checks - catches what tools miss; some manual effort per release.
  - B. WCAG 2.2 AA, automated only - cheap; automated tools find only roughly a third to a half of issues, misses chat-specific problems.
  - C. AAA - impractical site-wide.
- **Decision:** A. angular-eslint template a11y rules; axe-core in Playwright CI; manual keyboard / VoiceOver / NVDA / 200% zoom checklist per release. Chat rules: announce completed replies via polite live region (`aria-busy` while streaming), never move focus on new messages, focus not obscured by the widget, 24x24 px targets, timeout warnings, OTP paste/autofill, no redundant entry, reduced motion, semantic HTML for rich blocks.
- **Consequences:** Manual testing effort each release. Custom chat components need explicit a11y tests. Timeout warning UI required in both apps.

## ADR-026 - LLM metering and token budgets
- **Context:** The LLM must be treated as a paid production service, including locally on Ollama. Need cost visibility, enforced budgets and safe behavior when budgets are hit. docs/00 already planned a model gateway.
- **Options considered:**
  - A1. Agent code only - nothing new to run, conversation-aware; we build pricing, spend tracking and rate limits.
  - A2. LiteLLM gateway only - built-in pricing, spend, budgets, rate limits, metrics, provider switching by config; not conversation-aware.
  - A3. Both, split by responsibility.
- **Decision:** A3. LiteLLM: price table (shadow prices for local models), spend tracking, global daily USD budget, per-model rate limits, metrics. Agent LLM client: per-turn, per-conversation, per-customer caps (Redis), per-call recording, degradation ladder (alert 80% -> fallback model 90% -> no generation + FAQ + handoff at 100%). All model calls go through LiteLLM.
- **Consequences:** One more platform component (not a deployable; ADR-016 unchanged). Switching Ollama -> hosted model is config only. Verify which LiteLLM features (budgets, Prometheus metrics) are in the open-source edition before implementation.

## ADR-027 - LLM observability in the UI
- **Context:** Architect wants LLM latency, speed, tokens and cost visible inside the project, per conversation and system-wide.
- **Options considered:**
  - B1. Grafana only - standard, alerting, no UI code; aggregates only, outside the app.
  - B2. staff-console AI Operations only - in-app, per-conversation drill-down; must build charts, no alerting.
  - B3. Both, plus a developer overlay in customer-web.
- **Decision:** B3. Grafana for trends, NFR percentiles, spend and alerts. staff-console AI Operations (role `ops-admin`): live summary, conversation explorer with per-stage breakdown, read-only budget/pricing view. customer-web dev overlay from `message.metrics`, off by default. Contract additions (backward compatible, `v` stays 1): `status.updated`, `message.metrics`.
- **Consequences:** New BFF `ops` module and staff-console area; new Keycloak role; agent usage tables (`turns`, `llm_calls`). Open: chart library for AI Operations (docs/01).

## ADR-011 - Vector store
- **Context:** Hybrid retrieval (dense + keyword, RRF, rerank) over product pages, specs, policies and FAQs: ~5k-50k chunks, small even at 10x. Checkout availability target is 99.99% (docs/00 section 7).
- **Options considered:**
  - A. Postgres + pgvector (HNSW) + Postgres full-text - no new stateful system, metadata and vectors in one SQL query, transactional; keyword ranking is not BM25, shares Postgres with orders.
  - B. Qdrant - strong filtered and hybrid search, quantization, horizontal scale; extra system to run, sync from Postgres, strengths unused at our size.
  - C. OpenSearch / Elasticsearch - best BM25 and analyzers; heavy JVM footprint on the local machine, most operations work.
- **Decision:** A. Retrieval behind one retriever interface in `buywise-agent`. If Ragas shows weak exact-term retrieval, add ParadeDB `pg_search` (BM25 in Postgres). In production, RAG reads run on a read replica (or separate database), never on the primary serving checkout - detailed with ADR-010 / docs/07.
- **Consequences:** One database to operate; text and vectors always consistent. Moving to Qdrant later only replaces the retriever implementation and indexing job.

## ADR-010 - PostgreSQL organisation
- **Context:** Postgres holds business data (`buywise-services`), agent data and vectors (`buywise-agent`), and platform tool data (Keycloak, LiteLLM, Langfuse). Checkout needs 99.99% and RPO 0; the agent produces bursty checkpoint writes and vector searches. ADR-011 requires RAG reads off the primary serving checkout.
- **Options considered:**
  - A. One database, schema per module, everything in it - simplest; AI load competes with checkout, later split needs migration.
  - B. Database per deployable, grouped into clusters by criticality - isolation, clear ownership, light locally; more databases/users, two clusters in production.
  - C. Cluster per deployable everywhere - most isolation; too heavy for the local machine, beyond NFR needs.
- **Decision:** B.
  - Databases: `services` (schemas per module), `agent` (schemas `agent`, `knowledge`), `keycloak`, `litellm`, `langfuse`; one Postgres user per database, access only to its own.
  - Production: business cluster (`services`, `keycloak`) with synchronous replica (RPO 0); AI cluster (`agent`, `litellm`, `langfuse`) with read replica for RAG.
  - Local: one CloudNativePG cluster hosting all databases with the same names and users; production split is connection-string config only (ADR-013).
  - Inside `services`: one app user; no cross-schema joins or foreign keys, enforced by Spring Modulith verification and tests.
- **Consequences:** AI load cannot affect checkout. More databases and credentials to manage (ties to secrets decision, docs/08). Other deployables read business data only via REST or events.

## ADR-028 - Identity propagation
- **Context:** User identity must reach `buywise-services` through BFF -> agent -> `buywise-mcp`. The LLM chooses tools and arguments and can be steered by prompt injection. The MCP spec forbids token passthrough. Draft tools took `customer_id` as an argument.
- **Options considered:**
  - A. Pass the user token through - simplest; one token valid everywhere; MCP token passthrough anti-pattern.
  - B. Service accounts + user id header - simple; services trust any claimed user (confused deputy).
  - C. Token exchange per hop (RFC 8693, "on-behalf-of") - audience-restricted, scope-narrowed, short-lived JWTs with `act` delegation chain; extra Keycloak calls (cached), more config.
  - D. Own internal signed token minted by the BFF (Passport-style) - fast; custom protocol and key management, does not fit MCP OAuth.
- **Decision:** C. Rules: identity never a tool argument (`customer_id` removed from tools, taken from `sub`); scopes narrowed per hop and per intent; exchanged tokens ~5 min, cached in memory only, never in checkpoints/logs/traces; guests get public scopes + own cart, OTP gives a short-lived grant for that contact's orders; staff actions go BFF -> services directly; services log `sub` + `act` chain on writes. Services verify JWTs locally via JWKS.
- **Consequences:** A leaked token is useless outside its audience and few minutes; full delegation audit trail. More Keycloak configuration. Verify Keycloak's support for the `act` claim in standard token exchange before implementation; if partial, add the actor chain via a Keycloak protocol mapper. In production, mTLS (service mesh, future) would add workload identity; locally JWTs carry it.

## ADR-029 - Agent output path to the browser
- **Context:** NFR 7.2 #6: if a BFF pod dies mid-reply, the reply must complete after reconnect. Any design where the agent streams through a specific BFF pod loses the rest of the reply.
- **Options considered:**
  - A. Agent emits ADR-024 events over a streaming HTTP response to the BFF - simple; reply dies with the BFF pod.
  - B. Agent emits its own format, BFF maps it - agent independent of UI contract; same pod-death problem plus a mapping layer.
  - C. Agent appends ADR-024 events to the conversation's Redis Stream; BFF only reads - reply independent of BFF pods.
- **Decision:** C. `POST /turns` returns 202 and the turn runs in the background; events go to `conv:{id}` (capped by count and time); BFF also appends its own events (staff messages, handoff, tickets) there; one shared stream reader per BFF pod; SSE `id` = stream entry id; cancel via `POST /turns/{id}/cancel`.
- **Consequences:** NFR #6 met by design; one mechanism for delivery and replay (replaces pub/sub + replay buffer). Agent depends on Redis (already used for budgets). Amends ADR-020 (cross-pod mechanism) and ADR-024 rule 3 (`seq` removed from the envelope; SSE id is the stream entry id). Staff console composite cursor detailed at implementation. Same pattern as LangGraph Server's background runs with a joinable stream.

## ADR-030 - Intent routing
- **Context:** Router runs first on every turn; it drives handler choice, per-intent tool scoping and per-intent token scopes (ADR-028). Targets: system overhead <= 300 ms and first token < 1 s (NFR 5), accuracy >= 95% (NFR 8), ~400k turns/day. Must handle follow-ups and multi-intent messages.
- **Options considered:**
  - A. LLM classifier - context-aware, multi-intent, no training data; +200-500 ms and cost on every turn.
  - B. Small trained classifier - ~10-30 ms, near free, deterministic; needs labelled data, retraining, weak on context.
  - C. No router, one agent with all tools - simplest; loses tool and scope narrowing, more tokens, harder to evaluate.
  - D. Cascade: rules -> fast classifier -> LLM classifier.
- **Decision:** D. Clarifying question on low confidence, then handoff (also on negative sentiment). Flow stickiness for checkout and OTP. Multi-intent handled in order. Every decision logged in `router_decisions` and shown in AI Operations. Phase 1 rules + LLM and the eval set; phase 2 trains and enables the fast classifier.
- **Consequences:** Most turns routed in ~20 ms at near-zero cost once phase 2 lands; LLM reserved for hard cases. Two models to maintain plus thresholds to tune. Eval set doubles as training data.

## ADR-031 - MCP server layout
- **Context:** 12 tools across catalog, inventory, order, customer, helpdesk inside the `buywise-mcp` deployable. Agent scopes tools per intent (ADR-030); checkout needs high availability.
- **Options considered:** A. One server with all tools - simplest; one failure domain, no per-domain isolation. B. One server per domain in one process - per-intent connections, per-path limits/logs, optional per-domain Deployment by config; several client connections. C. Separate deployable per domain - breaks ADR-016, five pipelines for a thin layer.
- **Decision:** B. `/mcp/{domain}` paths, one image; single audience `buywise-mcp` with per-tool scopes.
- **Consequences:** Clear tool structure and isolation option without new deployables. Agent manages per-server discovery caching.

## ADR-032 - Tool rate limits
- **Context:** Must stop agent loops (bugs, prompt injection), user abuse (OTP brute force) and overload; no single layer sees all three.
- **Decision:** Four layers - agent (8 tool calls/turn, 3 identical in a row), Envoy (global per tool via `Mcp-Name`), MCP (per user/guest per tool, Redis token buckets: OTP 3/15 min per contact and IP, checkout 5/min, tickets 3/hour/conversation, reads 60/min), services (Bucket4j). Local: per-user limits unchanged, global / S. Limit hit -> structured error with `retryAfter`, explained to the customer, no retry loop.
- **Consequences:** Defence in depth; more limits to tune and monitor (Grafana). Redis becomes part of the MCP request path.

## ADR-033 - Data sources
- **Context:** Learning project needing accurate, realistic data for the catalog, RAG, evals and tests. No external business data exists; nothing may be scraped or copied verbatim.
- **Decision:**
  - Catalog: curated real product lineup (one maker first, others later) as our own JSON by category; real model names, specs, list prices and compatibility, verified by web search at generation; `specs_verified` date; maker never named (`brand_id` only); no source URLs.
  - Descriptions: facts in our own wording, never copied text.
  - Images: none; placeholders only.
  - Knowledge docs: spec sheets, product overviews and store info generated from seed data (single source of truth); policies, FAQs, how-to guides written and reviewed; a few PDFs for the Docling path.
  - Customers, orders, tickets: Faker with fixed seeds and designed edge cases. Eval sets built from the docs and reviewed.
  - Reproducible loading via `make seed` and `make ingest`.
- **Consequences:** Same data everywhere; no personal data; data changes reviewed like code. Spec accuracy depends on verification at generation time; re-verify when the lineup changes.

## ADR-034 - RAG chunking
- **Context:** Doc types differ (tables, sections, Q&A pairs, steps, records). Chunk boundaries drive retrieval precision and citation quality.
- **Options considered:** A. Fixed-size chunks - simple; splits tables and Q&A, mixes topics. B. Structure-aware per doc type - meaningful units, real citations, deterministic; per-type rules to maintain. C. Semantic chunking - adaptive; costly, non-deterministic, mixed gains.
- **Decision:** B, plus parent-child retrieval, deterministic context headers, and metadata filters (incl. `brand_id`). Contextual retrieval (LLM-generated headers) only as a phase-2 experiment if Ragas shows gains. Prices/stock/availability stripped in cleaning.
- **Consequences:** High-precision retrieval with full context for the LLM. Rules per doc type; sizes are starting values tuned with Ragas.

## ADR-035 - Backup policy (design only)
- **Context:** NFR 10 (orders RPO 0 / RTO 15 min; others RPO 5 min / RTO 1 h). Production-scale operations are design only (docs/00 section 7.4).
- **Decision:** CloudNativePG continuous WAL archiving + daily base backups to object storage; PITR 30 days (business cluster), 14 days (AI cluster); weekly immutable copy in a separate account/region; monthly timed restore drill; backups encrypted. Redis and Kafka not backed up (ephemeral / replayable from outbox); configuration as code in Git; RAG index rebuildable.
- **Consequences:** Documented and explained, not run locally; local data reproducible from Git. Supersedes the earlier local restore-test target and local MinIO.

## ADR-036 - PII policy
- **Context:** Chats and profiles contain PII; production may send prompts to a hosted LLM; dumps, backups and SQL access can expose stored PII. Implemented locally (code-level techniques).
- **Options considered:**
  - A1. Send chat text to the LLM as is vs A2. Presidio reversible placeholders before every LLM call.
  - B1. Disk encryption only vs B2. Field-level envelope encryption with blind index.
- **Decision:** A2 and B2 (defence in depth: in transit to the LLM provider and at rest). Plus: 4-tier classification; masking in code and in the OTel Collector; staff masked view with audited reveal; least privilege; retention per NFR 11; audited export/deletion jobs.
- **Consequences:** LLM never sees raw PII; dumps/backups don't expose contact fields. ~10-30 ms per turn for detection; detection is imperfect, so log/trace masking stays as a second layer. Encrypted fields can't be searched or sorted in SQL except via the blind index. Key rotation procedure required.

## ADR-037 - Conversation ownership
- **Context:** On every customer message the BFF must know whether the bot or staff owns the conversation. docs/03 had `owner` in agent state, but ADR-028 says staff actions never go through the agent.
- **Options considered:** A. Helpdesk module owns it (business rule with business data, audited), BFF caches in Redis. B. Agent owns it - forces staff actions through the agent, agent becomes a system of record. C. BFF owns it in Redis only - not durable, not audited.
- **Decision:** A. Accept -> owner staff; release/resolve -> owner bot; changes audited in `conversation_ownership`. BFF caches `conv:{id}:owner`, updated on accept/release and refreshed from helpdesk events. BFF pauses/resumes the agent; agent refuses turns while paused.
- **Consequences:** Single source of truth with audit. Cache must stay consistent with services (update on write + event refresh; on cache miss read from services).

## ADR-038 - AI Operations chart library
- **Context:** staff-console AI Operations (ADR-027) needs time series with target lines, spend gauge, per-stage waterfall, histograms. Loaded only by `ops-admin`, lazily; WCAG 2.2 AA (ADR-025).
- **Options considered:** A. Apache ECharts - richest, canvas, aria module, themeable; ~150 KB gz modular. B. Chart.js - small, simple; plugins for waterfall/gauge/zoom, no built-in a11y. C. ngx-charts - Angular-native SVG; historically slow upgrades, SVG slow on large data. D. Embedded Grafana panels - no chart code; cross-site embedding and auth, style mismatch, no per-conversation data.
- **Decision:** A, with our own ~50-line signal-based wrapper (no `ngx-echarts` dependency); theme from Material 3 tokens; "view as table" toggle rendering a semantic HTML table per chart.
- **Consequences:** Full chart capability in an admin-only lazy chunk; upgrades not blocked by a third-party wrapper; we maintain the wrapper.
