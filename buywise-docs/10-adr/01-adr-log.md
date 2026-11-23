# Architecture Decision Log - agent-buywise-shop

| ADR | Decision | Status | Date |
|---|---|---|---|
| ADR-001 | One monorepo with modules | Accepted | 2026-10-28 |
| ADR-002 | Java for business services, Python for AI and MCP, TypeScript for UI/Node server | Accepted | 2026-10-28 |
| ADR-003 | Angular 22 for the web UI (chosen over 21: stable signal APIs, longer support) | Accepted | 2026-10-28 |
| ADR-004 | NestJS 11 + Fastify Node server on Node.js 24 LTS; serves the Angular build (one deployable). Built on NestJS 12 (current major, 2026-10-30) | Accepted | 2026-10-28 |
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
| ADR-021 | Session pattern: Node server session (token handler), tokens in Redis, opaque `__Host-` cookie; guest sessions; separate staff session with MFA | Accepted | 2026-10-28 |
| ADR-022 | UI state: NgRx SignalStore for shared/live state, plain signals for local state, `httpResource` for read-only server data | Accepted | 2026-10-28 |
| ADR-023 | UI rendering: hybrid per route - prerender product/category pages, client rendering elsewhere; no per-request SSR | Accepted | 2026-10-28 |
| ADR-024 | Chat message contract: own versioned JSON Schema envelope, AG-UI-shaped reply events, structured blocks, Redis Stream replay (amended by ADR-029: SSE id = stream entry id, `seq` removed), idempotent sends | Accepted | 2026-10-28 |
| ADR-025 | Accessibility: WCAG 2.2 AA enforced by angular-eslint + axe-core in CI plus a manual per-release checklist; chat-specific rules | Accepted | 2026-10-28 |
| ADR-026 | LLM metering and budgets: LiteLLM model gateway (pricing, spend, global budget, rate limits) + agent LLM client (per-turn/conversation/customer caps, degradation); shadow pricing locally | Accepted | 2026-10-28 |
| ADR-027 | LLM observability in the UI: Grafana for trends/alerts + staff-console AI Operations (ops-admin) + customer-web dev overlay; `status.updated` and `message.metrics` events | Accepted | 2026-10-28 |
| ADR-028 | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop Node server -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-lived JWTs with `act` chain; identity never a tool argument | Accepted | 2026-10-28 |
| ADR-029 | Agent output path: background turns (`POST /turns` 202); agent appends ADR-024 events to per-conversation Redis Stream; Node server pods read and forward; replaces pub/sub and separate replay buffer | Accepted | 2026-10-28 |
| ADR-030 | Intent routing: cascade of rules -> fast in-process classifier -> economy-tier LLM classifier; clarify then handoff on low confidence; flow stickiness; decisions logged | Accepted | 2026-10-28 |
| ADR-031 | MCP layout: one server per domain (`/mcp/{domain}`) in one process and image; agent connects per intent; optional per-domain Deployment in production | Accepted | 2026-10-28 |
| ADR-032 | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j | Accepted | 2026-10-28 |
| ADR-033 | Data sources: curated real product lineup (names, specs, list prices; maker never named, `brand_id` only), generated and written knowledge docs (multiple formats, amended by ADR-039), Faker customers/orders, fixed seeds, no images | Accepted | 2026-10-28 |
| ADR-034 | RAG chunking: structure-aware per doc type, parent-child retrieval, context headers, metadata filters; sizes tuned with Ragas; applied to the ADR-039 Document model | Accepted | 2026-10-28 |
| ADR-035 | Backup policy (design only): Postgres WAL archiving + daily base backups, PITR 30/14 days, immutable off-site weekly copy, monthly restore drill; Redis/Kafka not backed up; config in Git; no local backups | Accepted | 2026-10-28 |
| ADR-036 | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; masked logs/traces; audited staff reveal; retention and privacy-rights jobs | Accepted | 2026-10-28 |
| ADR-037 | Conversation ownership owned by the helpdesk module in `buywise-services`; Node server caches in Redis; agent paused/resumed as second check | Accepted | 2026-10-28 |
| ADR-038 | AI Operations charts: Apache ECharts (modular imports) with own thin signal-based wrapper; "view as table" accessibility toggle | Accepted | 2026-10-28 |
| ADR-039 | Multi-format ingestion: detect by magic bytes -> parser plugin per format -> common Document model with provenance -> normalize, validate, clean, chunk; quarantine; golden tests; worker inside agent deployable | Accepted | 2026-10-28 |
| ADR-040 | Embeddings: bge-m3 in every environment via LiteLLM; `model_version` per vector; PII-masked queries; phase-3 bake-off; model change via blue/green re-index | Accepted | 2026-10-28 |
| ADR-041 | Gradle (Kotlin DSL) with a version catalog for all Java deployables (services, event publisher, event consumers) | Accepted | 2026-10-29 |
| ADR-042 | uv for every Python project: `pyproject.toml` + committed `uv.lock` + `.python-version`; `uv sync --locked` locally and in CI | Accepted | 2026-10-29 |
| ADR-043 | Product `availability` = sale status only (`available` / `preorder` / `discontinued`), owned by catalog, DB CHECK + contract enum; preorder ship date = `release_date`; stock only from inventory | Accepted | 2026-10-30 |
| ADR-044 | Chat events: strict when writing, tolerant when reading - writers validate against the schema before sending; readers ignore unknown fields and unknown event types | Accepted | 2026-10-30 |
| ADR-045 | Hardware factor k = single-stream LLM speed factor; capacity under load is a separate test; `buywise-deploy/local/scale.yaml` holds S and k | Accepted | 2026-10-30 |
| ADR-046 | All database scripts in one module, `buywise-db` (cluster init, migrations and seed per database); apps read their migrations from there | Accepted | 2026-11-18 |
| ADR-047 | Top-level layout: every top-level folder is `buywise-*` (data, deploy, docs -> `buywise-data`, `buywise-deploy`, `buywise-docs`); local run scripts + logs in `buywise-deploy/local/`; Node server folder `buywise-web/server/` | Accepted | 2026-11-18 |
| ADR-048 | All documentation in `buywise-docs/`: application-level at its top, module docs in `buywise-docs/NN-<module>/`; modules keep only README.md (+ code, Makefile); numbered in reading order (00 overview, 01-08 modules, 09 roadmap, 10 ADRs, 11 learning, 12 archive; files 01, 02, ... inside each folder) | Accepted | 2026-11-18 |
| ADR-049 | Customer sign-up: Google login (Keycloak identity provider) or Keycloak-hosted register form; email verification for form sign-ups (Mailpit locally); `customers` row created on first login; same-email accounts linked only after the user proves ownership | Accepted (build after deep dive) | 2026-11-22 |
| ADR-050 | MCP authorization (M1): MCP servers are OAuth resource servers (spec 2026-07-28); token exchange per hop (agent -> `aud: buywise-mcp`, MCP -> `aud: buywise-services`), never token passthrough; per-tool scopes; issuer check (RFC 9207); guests use the agent's own read-only token; CIMD deferred to third-party clients | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-051 | Identity in MCP tools (M2): `Resolve(fn)` builds `Customer` from the validated token; declared in each tool signature, invisible to the model; scope checked in the resolver; a test fails if an orders tool lacks it | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-052 | Confirmation in MCP (M3): `place_order` and `cancel_order` always confirm through multi round-trip `input_required` + `Elicit`; agent pauses/resumes the turn; chat buttons via new contract events; price lock on resume; 15-min expiry; `quoteId` is the idempotency key | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-053 | MCP tool annotations (M4): every tool annotated (readOnly / destructive / idempotent / openWorld); agent policy driven by them (non-read-only -> confirmation, read-only/idempotent -> retry, read-only -> per-turn cache); a test checks annotations match behaviour | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-054 | MCP structured output (M5): every tool returns a Pydantic model -> generated `outputSchema`, `structuredContent` enforced, text summary kept; agent builds cards from structured content; schemas snapshot-tested | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-055 | MCP errors (M6): typed tool errors (`code`, `message`, `retryable`, `hint`); MCP maps service HTTP codes; AI hints move from services to MCP; 5xx/timeouts retryable + circuit breaker; no internals reach the model; protocol errors only for protocol faults | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-056 | MCP per-tool control (M7): no internal gateway kept; MCP middleware reads `Mcp-Method`/`Mcp-Name` for per-tool rate limits (Redis, ADR-032), metrics, logs and a kill switch | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-057 | MCP caching (M8): tool lists cacheable (`ttlMs` 10 min, shared `cacheScope`), refreshed on new server version; read-only tool results cached within one turn | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-058 | MCP resources (M9): `buywise://stores`, `buywise://stores/{id}`, `buywise://catalog/categories` (inventory/catalog servers) and `buywise://policies/{doc}` (new knowledge server, reads the published documents, not the agent database); agent loads stores as a resource; citations link to resource URIs; RAG search stays in the agent | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-059 | MCP prompts (M10): domain prompts (e.g. `compare_products`, `order_help`) live on their MCP servers, versioned with the tools; used by the intent router (ADR-030) and staff console quick actions; agent keeps only its core system prompt | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-060 | MCP Tasks (M11): new `/mcp/helpdesk` server; `request_staff_handoff` runs as a Task (queued -> accepted -> ended) mapped to `handoff.*` chat events; built with the staff console (phase 5) | Accepted (build in phase 5) | 2026-11-22 |
| ADR-061 | MCP Apps (M12): hybrid - native product and confirmation cards stay (ADR-024/025); one MCP App widget (product comparison with variant picker) in a sandboxed iframe via a new `block.app` chat event | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-062 | MCP utilities (M13): progress -> `status.updated`; agent cancels in-flight tool calls on stop/leave; cursor paging for `list_my_orders` and `search_products`; structured server logs to observability, not MCP log messages | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-063 | MCP observability (M14): OpenTelemetry built with the MCP phase - `traceparent` agent -> MCP -> services, SDK per-tool spans, hashed customer ids, local collector + trace viewer | Accepted (build in MCP production phase) | 2026-11-22 |
| ADR-064 | MCP tool versioning and testing (M15): snapshots of names/descriptions/schemas/annotations in CI, breaking change = new tool name or server version, integration tests (SDK Client + Testcontainers), MCP Inspector, tool-choice evals on description changes | Accepted (build in MCP production phase) | 2026-11-22 |

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
- **Context:** Browser needs streamed agent replies, live staff-takeover messages, ticket queue updates and order status pushes. Traffic is mostly server -> browser; customers send occasional messages. Two Node server pods behind Envoy.
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
  - A. Node server session / token handler - tokens server-side in Redis, opaque httpOnly cookie; recommended by IETF "OAuth 2.0 for Browser-Based Applications"; needs session store and CSRF protection.
  - B. Tokens in the Angular app (public client) - no server sessions; tokens exposed to XSS, refresh token in browser, awkward with SSE.
  - C. Encrypted tokens in the cookie - no store; 4 KB cookie limit, hard server-side revocation.
- **Decision:** A. Authorization Code + PKCE in the Node server; Redis session store; `__Host-` `HttpOnly` `Secure` `SameSite=Lax` cookie; guest sessions upgraded on login with session id rotation; separate staff client and cookie scoped to `/staff`, `/api/staff`, shorter idle timeout, MFA; CSRF via SameSite + custom header.
- **Consequences:** Tokens never reach the browser; SSE works with the cookie. Node server owns refresh and logout. Redis becomes critical for login state (already used for pub/sub). Identity propagation to agent/MCP is an open item in buywise-docs/03-buywise-agent/01-design.md and buywise-docs/04-buywise-mcp/01-design.md.

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
  - B. SSR for customer-web - fast and indexable everywhere; Node server renders every request, all shared code must be server-safe, no gain on personal pages.
  - C. Hybrid per route - prerender product/category pages, client rendering for the rest.
- **Decision:** C. Angular per-route render modes: Prerender for product/category, Client for chat/cart/checkout/account and all of staff-console. No per-request SSR.
- **Consequences:** Node server stays a file server; prerendered output suits the future CDN option. Price/stock must be fetched live on product pages. Catalog content changes need a rebuild. Prerendered code must guard browser-only APIs. Upgrade path: Server render mode for product routes.

## ADR-024 - Chat message contract
- **Context:** The SSE stream and message POSTs are the central UI interface, used by the agent, Node server and both apps. It carries agent and non-agent events (staff messages, tickets, order status).
- **Options considered:**
  - A. Own typed contract - covers all event kinds, explicit versioning; we maintain it.
  - B. AG-UI protocol - published standard with TS/Python SDKs; agent events only, community Angular support, still evolving.
  - C. Forward raw LangGraph events - no mapping; leaks internals, UI breaks on graph refactors.
- **Decision:** A, with agent-reply events shaped like AG-UI start/content/end. Versioned envelope (`v`, `type`, `ts`, `conversationId`, `messageId`, `payload`); structured `block.*` content rendered by components; sanitized Markdown for text; Redis Stream replay keyed by the SSE `id` / `Last-Event-ID`, where the SSE `id` is the Redis Stream entry id (amended by ADR-029: the original `seq` envelope field was removed); `clientMessageId` for idempotent sends; JSON Schema in `shared/contracts/` generating TS and Pydantic types, drift checked in CI.
- **Consequences:** One contract across Python and TypeScript; adoption of AG-UI remains possible. We own schema evolution. The open item "agent emits contract events directly or the Node server maps them" was resolved by ADR-029: the agent emits ADR-024 events directly to the conversation's Redis Stream.

## ADR-025 - Accessibility
- **Context:** US online store (WCAG 2.x AA is the de facto ADA benchmark). Custom chat UI with streaming text, overlays, OTP and session timeouts.
- **Options considered:**
  - A. WCAG 2.2 AA, automated + manual checks - catches what tools miss; some manual effort per release.
  - B. WCAG 2.2 AA, automated only - cheap; automated tools find only roughly a third to a half of issues, misses chat-specific problems.
  - C. AAA - impractical site-wide.
- **Decision:** A. angular-eslint template a11y rules; axe-core in Playwright CI; manual keyboard / VoiceOver / NVDA / 200% zoom checklist per release. Chat rules: announce completed replies via polite live region (`aria-busy` while streaming), never move focus on new messages, focus not obscured by the widget, 24x24 px targets, timeout warnings, OTP paste/autofill, no redundant entry, reduced motion, semantic HTML for rich blocks.
- **Consequences:** Manual testing effort each release. Custom chat components need explicit a11y tests. Timeout warning UI required in both apps.

## ADR-026 - LLM metering and token budgets
- **Context:** The LLM must be treated as a paid production service, including locally on Ollama. Need cost visibility, enforced budgets and safe behavior when budgets are hit. buywise-docs/00 already planned a model gateway.
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
- **Consequences:** New Node server `ops` module and staff-console area; new Keycloak role; agent usage tables (`turns`, `llm_calls`). Open: chart library for AI Operations (buywise-docs/01-buywise-web/01-design.md).

## ADR-011 - Vector store
- **Context:** Hybrid retrieval (dense + keyword, RRF, rerank) over product pages, specs, policies and FAQs: ~5k-50k chunks, small even at 10x. Checkout availability target is 99.99% (buywise-docs/00 section 7).
- **Options considered:**
  - A. Postgres + pgvector (HNSW) + Postgres full-text - no new stateful system, metadata and vectors in one SQL query, transactional; keyword ranking is not BM25, shares Postgres with orders.
  - B. Qdrant - strong filtered and hybrid search, quantization, horizontal scale; extra system to run, sync from Postgres, strengths unused at our size.
  - C. OpenSearch / Elasticsearch - best BM25 and analyzers; heavy JVM footprint on the local machine, most operations work.
- **Decision:** A. Retrieval behind one retriever interface in `buywise-agent`. If Ragas shows weak exact-term retrieval, add ParadeDB `pg_search` (BM25 in Postgres). In production, RAG reads run on a read replica (or separate database), never on the primary serving checkout - detailed with ADR-010 / buywise-docs/06-buywise-db/01-design.md.
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
- **Consequences:** AI load cannot affect checkout. More databases and credentials to manage (ties to secrets decision, buywise-docs/08-buywise-deploy/01-design.md). Other deployables read business data only via REST or events.

## ADR-028 - Identity propagation
- **Context:** User identity must reach `buywise-services` through Node server -> agent -> `buywise-mcp`. The LLM chooses tools and arguments and can be steered by prompt injection. The MCP spec forbids token passthrough. Draft tools took `customer_id` as an argument.
- **Options considered:**
  - A. Pass the user token through - simplest; one token valid everywhere; MCP token passthrough anti-pattern.
  - B. Service accounts + user id header - simple; services trust any claimed user (confused deputy).
  - C. Token exchange per hop (RFC 8693, "on-behalf-of") - audience-restricted, scope-narrowed, short-lived JWTs with `act` delegation chain; extra Keycloak calls (cached), more config.
  - D. Own internal signed token minted by the Node server (Passport-style) - fast; custom protocol and key management, does not fit MCP OAuth.
- **Decision:** C. Rules: identity never a tool argument (`customer_id` removed from tools, taken from `sub`); scopes narrowed per hop and per intent; exchanged tokens ~5 min, cached in memory only, never in checkpoints/logs/traces; guests get public scopes + own cart, OTP gives a short-lived grant for that contact's orders; staff actions go Node server -> services directly; services log `sub` + `act` chain on writes. Services verify JWTs locally via JWKS.
- **Consequences:** A leaked token is useless outside its audience and few minutes; full delegation audit trail. More Keycloak configuration. Verify Keycloak's support for the `act` claim in standard token exchange before implementation; if partial, add the actor chain via a Keycloak protocol mapper. In production, mTLS (service mesh, future) would add workload identity; locally JWTs carry it.

## ADR-029 - Agent output path to the browser
- **Context:** NFR 7.2 #6: if a Node server pod dies mid-reply, the reply must complete after reconnect. Any design where the agent streams through a specific Node server pod loses the rest of the reply.
- **Options considered:**
  - A. Agent emits ADR-024 events over a streaming HTTP response to the Node server - simple; reply dies with the Node server pod.
  - B. Agent emits its own format, Node server maps it - agent independent of UI contract; same pod-death problem plus a mapping layer.
  - C. Agent appends ADR-024 events to the conversation's Redis Stream; Node server only reads - reply independent of Node server pods.
- **Decision:** C. `POST /turns` returns 202 and the turn runs in the background; events go to `conv:{id}` (capped by count and time); Node server also appends its own events (staff messages, handoff, tickets) there; one shared stream reader per Node server pod; SSE `id` = stream entry id; cancel via `POST /turns/{id}/cancel`.
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
- **Amendment (2026-11-22, ADR-058/060):** servers are catalog, inventory, order(s), customer, knowledge (policy resources) and helpdesk (Tasks). Built today: catalog, inventory, orders.

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
- **Context:** NFR 10 (orders RPO 0 / RTO 15 min; others RPO 5 min / RTO 1 h). Production-scale operations are design only (buywise-docs/00 section 7.4).
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
- **Context:** On every customer message the Node server must know whether the bot or staff owns the conversation. buywise-docs/03-buywise-agent/01-design.md had `owner` in agent state, but ADR-028 says staff actions never go through the agent.
- **Options considered:** A. Helpdesk module owns it (business rule with business data, audited), Node server caches in Redis. B. Agent owns it - forces staff actions through the agent, agent becomes a system of record. C. Node server owns it in Redis only - not durable, not audited.
- **Decision:** A. Accept -> owner staff; release/resolve -> owner bot; changes audited in `conversation_ownership`. Node server caches `conv:{id}:owner`, updated on accept/release and refreshed from helpdesk events. Node server pauses/resumes the agent; agent refuses turns while paused.
- **Consequences:** Single source of truth with audit. Cache must stay consistent with services (update on write + event refresh; on cache miss read from services).

## ADR-038 - AI Operations chart library
- **Context:** staff-console AI Operations (ADR-027) needs time series with target lines, spend gauge, per-stage waterfall, histograms. Loaded only by `ops-admin`, lazily; WCAG 2.2 AA (ADR-025).
- **Options considered:** A. Apache ECharts - richest, canvas, aria module, themeable; ~150 KB gz modular. B. Chart.js - small, simple; plugins for waterfall/gauge/zoom, no built-in a11y. C. ngx-charts - Angular-native SVG; historically slow upgrades, SVG slow on large data. D. Embedded Grafana panels - no chart code; cross-site embedding and auth, style mismatch, no per-conversation data.
- **Decision:** A, with our own ~50-line signal-based wrapper (no `ngx-echarts` dependency); theme from Material 3 tokens; "view as table" toggle rendering a semantic HTML table per chart.
- **Consequences:** Full chart capability in an admin-only lazy chunk; upgrades not blocked by a third-party wrapper; we maintain the wrapper.

## ADR-039 - Multi-format document parsing
- **Context:** Main learning goal: real parsing techniques across formats, not "chunk the PDF". Knowledge docs are created in DOCX, digital PDF, scanned PDF/PNG, HTML, XLSX/CSV, PPTX, EML with attachments, Markdown/TXT and generated JSON. Amends ADR-033 (formats).
- **Options considered:** A. Docling for everything - least code; hides techniques, no email, weak boilerplate removal. B. Own parser per format from low-level libraries - most learning; rebuilds hard problems (PDF tables, OCR) badly. C. Own plugin system with a common Document model and best-fit library per format.
- **Decision:** C. Pipeline detect (magic bytes) -> parse (plugin per format) -> normalize -> validate (OCR retry, confidence) -> clean (prices) -> chunk (ADR-034 on the Document model) -> embed/index. Elements carry provenance (page+bbox, sheet!row, slide, DOM path, attachment). Quarantine for failures; golden snapshot tests per sample file; content-hash idempotency with parser version. Entry via `buywise-data/inbox/` and ops-admin upload. Runs as an ingestion worker process inside `buywise-agent`.
- **Why not DoclingDocument as the common model:** page-based provenance and no first-class records; own model acts as an anti-corruption layer and lets us add/route other engines (managed document AI, VLM) via adapters. Details in buywise-docs/03-buywise-agent/02-rag.md section 3d.
- **Consequences:** New format = one plugin. Precise citations. More libraries to maintain (Docling, OCR engine, python-docx, openpyxl/pandas, python-pptx, trafilatura, markdown-it-py). OCR is CPU-heavy, isolated in the worker.

## ADR-040 - Embedding model
- **Context:** buywise-docs/03-buywise-agent/02-rag.md planned nomic-embed-text locally and bge-m3 in production - different dimensions, prefixes and quality, breaking the "same system, scaled down" rule. Query and document vectors must come from the same model and version.
- **Options considered:** nomic-embed-text v1.5 (small, fast, prefixes, English); bge-m3 (proven, multilingual, dense+sparse+multi-vector, no prefixes); mxbai-embed-large (strong English, 512 max input); snowflake-arctic-embed2 (strong, less adopted); Qwen3-Embedding-0.6B (top 2025 benchmarks, newer); hosted-only APIs (cannot run locally).
- **Decision:** bge-m3 (1024 dims) everywhere from phase 0, called through LiteLLM; `model_version` stored per vector; queries PII-masked before embedding (ADR-036). Phase-3 bake-off vs Qwen3-Embedding-0.6B and nomic-embed-text v1.5 on our eval set decides the final model.
- **Consequences:** Local retrieval evals predict production. Changing model is a blue/green migration: new vector column, background re-embed, eval, switch by flag, drop old. bge-m3 sparse output available as a future hybrid-search option.

## ADR-041 - Java build tool
- **Context:** `buywise-services` gets its build file in phase 1; `buywise-events` (publisher, consumers) in phase 4. Three Java deployables should share Spring Boot and library versions, and CI (phase 0 step 7) should stay fast.
- **Options considered:** A. Maven - declarative XML, fixed lifecycle, most common in Spring shops, easy to read; no real build cache, shared versions need a parent POM. B. Gradle with Kotlin DSL - build cache and incremental builds, clean multi-project builds, version catalog (`gradle/libs.versions.toml`) shared by all apps; steeper learning curve, build scripts can become clever code.
- **Decision:** B. Gradle Kotlin DSL, Gradle wrapper (`gradlew`) committed, one version catalog for all Java deployables; no custom build logic beyond convention plugins.
- **Open for phase 1:** build layout - one Gradle build containing services + events vs separate builds sharing the catalog (decided when the first build file is written).
- **Consequences:** Faster local and CI builds; one place to bump versions. Build scripts must be kept plain and reviewed like code.

## ADR-042 - Python environment and dependency manager
- **Context:** `buywise-agent` used pip + venv with unpinned dependencies and no lock file; `buywise-data/tools` used `requirements.txt` with loose pins; the Python version came from whatever `python3` was on PATH. Installs could differ between laptop, CI and later runs (including transitive dependencies), and pip installs were slow.
- **Options considered:** A. pip + pip-tools (`requirements.txt` compiled with hashes) - works, two tools and two file styles. B. Poetry - lock file, own dependency syntax and slower resolver. C. uv - reads standard `pyproject.toml`, cross-platform `uv.lock` with hashes, installs/pins Python itself, 10-100x faster than pip.
- **Decision:** C. Every Python project (`buywise-agent`, `buywise-mcp`, `buywise-data/tools`) has `pyproject.toml` + committed `uv.lock` + `.python-version` (3.12). Make targets use `uv sync --locked` / `uv run --locked` (fail if the lock file is out of date); upgrades are deliberate (`uv lock --upgrade`) and reviewed as a lock-file diff. CI uses the `astral-sh/setup-uv` action. Container images (phase 1+) install with `uv sync --locked --no-dev`.
- **Consequences:** Identical environments everywhere; CI catches a `pyproject.toml` change without a new lock. Developers need uv installed (`brew install uv`). `buywise-data/tools/requirements.txt` removed.

## ADR-043 - Product availability means sale status
- **Context:** The product card (ADR-024) had a free-text `availability`. In the catalog, `availability` is the product's sale status (49 `available`, one free-text `preorder (pre-orders from ..., ships ...)`), with no DB constraint; stock quantities live in the inventory module. A free-text field lets typos through and mixes concepts.
- **Options considered:** A. Sale status only, enum owned by catalog; stock stays in `stockAtStore.quantity`. B. Combined status (`available` / `low_stock` / `out_of_stock` / `preorder`) computed from catalog + inventory - needs a low-stock threshold rule and mixes two modules' data in one field. C. Enum in the contract only, DB left as free text.
- **Decision:** A. Values `available`, `preorder`, `discontinued`; Flyway V3 normalizes existing values and adds a CHECK constraint; contract enum + optional `shipsOn` (date). Preorder ship date is the existing `release_date` (no new column).
- **Consequences:** Typos rejected in the DB and in generated TS/Pydantic types. "Low stock" wording, if wanted later, is a UI or inventory rule on `quantity`, not a catalog value. Adding a status value means a migration + schema change.

## ADR-044 - Strict when writing, tolerant when reading
- **Context:** The chat contract (ADR-024) uses `additionalProperties: false` everywhere (catches typos) and promises that adding optional fields is safe. A reader that validates strictly breaks that promise: a browser tab open for hours, or a Node server pod not yet upgraded, would reject events from a newer writer. Writers: agent, Node server (staff/handoff/ticket events), services (order events). Readers: Node server (forwarding to SSE), browser.
- **Options considered:** A. Strict everywhere - simplest, but readers must always deploy before writers and old tabs fail until reload. B. Strict write, tolerant read. C. Tolerant everywhere (drop `additionalProperties: false`) - never breaks, but typos pass silently at the source.
- **Decision:** B. Writers validate every event against the generated strict models before appending to the stream (Pydantic `extra='forbid'` in Python; a runtime check in the Node server for its own events). The Node server, when forwarding, checks only the envelope (`v`, `type`, `conversationId`) and passes the rest through unchanged. The browser ignores unknown event types and unknown fields. An event with an unsupported `v` is skipped and logged, never crashes the client.
- **Consequences:** Adding optional fields and new event types stays safe in any deploy order. Typos are caught where they are made (contract test: an event with an unknown field is rejected by the writer models). Reader tolerance is tested in phase 1 when reader code exists (unknown field and unknown type are forwarded/ignored).

## ADR-045 - Hardware factor k: what it measures and where it lives
- **Context:** buywise-docs/00 section 7.1 multiplies model-dependent local limits by `k` (production tokens/s / local tokens/s). The phase 0 benchmark measures one reply streaming alone, while the local target has ~8 replies generating at once (NFR 1), which share one GPU and slow each other down. The docs also said `S` and `k` live in Helm `values-local.yaml`, which only arrives in phase 7; the benchmark writes `buywise-deploy/local/scale.yaml`.
- **Options considered:** Measurement - A. single stream (pure hardware speed); B. at local concurrency (one number mixing hardware speed and capacity). Location - A. `buywise-deploy/local/scale.yaml` as the only source, Helm values filled from it; B. move to `values-local.yaml` now; C. keep both by hand.
- **Decision:** Measurement A: `k` is the single-stream hardware factor (warm-up run + median of 5 runs through LiteLLM). Capacity - how many replies can generate at once before each drops below 50/k tokens/s - is a separate test with k6 in phase 7 and sets the agent admission limit. Location A: `buywise-deploy/local/scale.yaml` is the single source of `S` and `k`; phase 7 Helm `values-local.yaml` reads from it, never a hand-typed copy.
- **Consequences:** A slower reply under load shows up as a capacity problem, not hidden inside `k`. `make k` is rerun when the machine or local model changes. Real-turn TTFT (long prompts with retrieved context) is checked in phase 1, not by this benchmark.

## ADR-046 - All database scripts in one module
- **Context:** Database scripts were spread over four places: cluster init in `buywise-deploy/compose/postgres/init`, services migrations in `buywise-services/src/main/resources/db/migration`, seed SQL in `data/docs/walkthroughs`, and the `rag.chunks` table as a SQL string inside `buywise-agent` Python code. Hard to see what runs, when and against which database; the project rule was "scripts live in their own module".
- **Options considered:** A. Keep files in place, add one map document and `make` targets. B. Same folder shape (`db/migrations`, `db/seed`) inside each owner module. C. One module `buywise-db` with a folder per database.
- **Decision:** C. `buywise-db/database/` (databases, users, pgvector), `buywise-db/services/{01-ddl,02-dml,03-data}/` (ddl = Flyway structure, dml = seed load SQL, data = seed JSON), `buywise-db/agent`. Seed JSON moved from `data/seed` to `services/03-data` (2026-11-18); `data/tools` generators still produce it. Flyway runs per database (`make migrate`: containers `flyway` and `flyway-agent`); buywise-services packs `services/01-ddl` into its jar at `db/migration` (Gradle `processResources`); buywise-agent no longer creates tables; `make seed` loads the seed SQL. Exception to the module-owned-scripts rule, for database scripts only.
- **Consequences:** One place and one run order for every database object. Ownership per database is still clear from the folder (ADR-010 unchanged: database per deployable, own user). The services and agent builds depend on a sibling folder: production images must copy `buywise-db/<database>/ddl` in their build. The agent database now has Flyway history (`flyway.flyway_schema_history`).

## ADR-047 - Top-level project layout
- **Context:** After ADR-046 the root still mixed styles: `data/`, `deploy/` and `docs/` without the `buywise-` prefix (and `data/` without a single owner), root `scripts/` (local start/stop) and `logs/` (their output) outside any module, an empty `ui/`, the Node server folder still named `bff/` (a term dropped from the docs), and `.gitkeep` files left in folders that already had files.
- **Options considered:** A. Leave as is and document it. B. Move knowledge and eval sets into `buywise-agent` (but the generators also feed `buywise-db`). C. One naming rule: every top-level folder is `buywise-*`, including the project-wide ones.
- **Decision:** C. `data/` -> `buywise-data/` (knowledge, eval, inbox, tools; shared content and test data), `deploy/` -> `buywise-deploy/`, `docs/` -> `buywise-docs/`. `scripts/run-local.sh`, `scripts/stop-local.sh` -> `buywise-deploy/local/`; logs -> `buywise-deploy/local/logs/` (git-ignored). `buywise-web/bff/` -> `buywise-web/server/` (npm package `buywise-server`). `ui/` removed. `.gitkeep` kept only in folders meant to be empty (`buywise-data/inbox`, `buywise-events/*`).
- **Consequences:** The root reads as one list of `buywise-*` folders, plus tool folders whose names the tools fix (`.github` for GitHub Actions). `make` targets unchanged. Agent `knowledge_dir` default is `../buywise-data/knowledge`. Not to be confused with `PG_DATA_DIR` (`../buywise-data/postgres`, Postgres files outside the repo). Older notes and ADR-046 keep the paths of their time.

## ADR-048 - All documentation in buywise-docs
- **Context:** Each module had its own `docs/` folder (design.md, learning.md, rag.md, walkthroughs) while application-level docs lived in `buywise-docs/`. Reading the design meant hopping between nine folders.
- **Options considered:** A. Keep docs per module (earlier rule, 2026-10-30). B. Everything in `buywise-docs/`, including module READMEs. C. Everything in `buywise-docs/` except each module's README.md.
- **Decision:** C. `buywise-docs/` top: 00 overview, 09 roadmap, `adr/`, `learning/` (phase index, deep dive), `archive/`. Module docs: `buywise-docs/NN-<module>/` (same file names as before: design.md, learning.md, rag.md, walkthroughs/). Each module keeps its README.md - the page GitHub and the IDE open for the folder (what it is, how to run it, ADRs, links to its docs).
- **Numbering (amendment, 2026-11-18, architect):** folders and files carry a two-digit prefix in reading order, lowercase-with-hyphens: `00-architecture-overview.md`, `01-buywise-web/` ... `08-buywise-deploy/` (layer order web, services, agent, mcp, events, db, data, deploy), `09-implementation-roadmap.md`, `10-adr/`, `11-learning/`, `12-archive/`; inside a module folder `01-design.md` first and the learning notes last. The old references "docs/00" and "docs/09" keep their meaning.
- **Consequences:** One place to read and search all design and learning notes; the docs tree mirrors the module names. Module folders hold code, README, Makefile and scripts only. Supersedes the "docs inside the module" rule of 2026-10-30.

## ADR-049 - Customer sign-up (Google or form)
- **Context:** `registrationAllowed: false` and no sign-up flow, so only the demo user can log in; login fails with "No customer account" when no `customers` row exists. The architect wants new customers to sign up with their Google account or a sign-up form.
- **Options considered:**
  - Form: A. Keycloak-hosted register page - no password handling in our code (ADR-028), least work; look themed later. B. Own Angular form + Keycloak admin API - full control of look, but our code handles passwords and an admin credential.
  - Customer row: A. Created by the Node server callback on first login when missing - one path for Google and form. B. Keycloak event listener notifies services - needs a Keycloak extension, more moving parts.
  - Email check: A. Verify form sign-ups by email link (Mailpit container catches mail locally). B. No verification for now.
- **Decision:** Keycloak-hosted form (A); Google added as an identity provider in the `buywise` realm (Keycloak shows "Sign in with Google" and talks to Google); row on first login (A); email verification on (A). Same email from a second way in (form account, then Google) is linked only after the user proves they own the existing account (Keycloak first-broker-login flow), never silently. Build after the deep-dive week.
- **Consequences:** Node server login flow stays one OIDC login to Keycloak. Changes to make: realm `registrationAllowed: true`, `verifyEmail: true`, SMTP settings, Google identity provider (client id/secret in `compose/.env`, redirect `http://localhost:8080/realms/buywise/broker/google/endpoint`, created in the architect's Google Cloud console); Mailpit service in `compose.yaml`; services `POST /api/customers` (does not exist today); callback creates the row instead of failing, ideally keyed by the Keycloak user id (`sub`) as well as email; new users get the `customer` role by default. Local Google login needs internet access.

## ADR-050 - MCP authorization (M1)
- **Context:** Today the agent sends `X-Customer-Id` and MCP and services trust it; anyone who reaches ports 8090/8081 can act as any customer. The MCP spec 2026-07-28 treats an HTTP MCP server as an OAuth resource server: it validates a token on every request, rejects tokens not issued for it (audience), and must not pass the user's token on. The architect wants production-grade MCP built and learned hands-on.
- **Options considered:** A. Token exchange per hop (ADR-028) - spec-compliant, least privilege per hop, `act` audit chain; most moving parts. B. Pass the user token through - simple, forbidden by the spec, one stolen token works everywhere. C. Trusted service network + signed customer id - fewer Keycloak calls; MCP and services cannot verify the user; not standard MCP auth.
- **Decision:** A. Node server holds the user token; agent exchanges it at Keycloak (RFC 8693) for a token with `aud: buywise-mcp` and the turn's scopes; each MCP server validates signature (Keycloak JWKS), issuer (RFC 9207: only the `buywise` realm), audience and the tool's scope; MCP exchanges again for `aud: buywise-services`; services validates and checks ownership on `sub` (ADR-028). Scopes per tool: `catalog:read` (search_products, get_product), `inventory:read` (list_stores, check_stock), `orders:read` (list_my_orders, get_order, quote_order), `orders:write` (place_order, cancel_order). Guests (not logged in): the agent's own client-credentials token with `catalog:read` + `inventory:read` only. MCP publishes protected resource metadata so clients can discover the authorization server. CIMD (client metadata documents) not needed for our first-party agent (pre-registered in Keycloak); revisit for third-party MCP clients.
- **Consequences:** Replaces `X-Customer-Id` on agent -> MCP -> services. Needs: Keycloak token-exchange permissions for `buywise-agent` and `buywise-mcp` clients, client scopes in `buywise-realm.json`, JWT validation in MCP (Python) and Spring Security resource server in services, exchanged-token caching per conversation (short TTL). Two exchanges per turn add latency (cached). Local tests need real Keycloak tokens (helper script). Supersedes the "X-Customer-Id" simplification in buywise-docs/09 section 4 when built.

## ADR-051 - Identity in MCP tools (M2)
- **Context:** Today each orders tool calls `_customer(ctx)` by hand to read `X-Customer-Id`; a new tool that forgets it has no identity check. MCP Python SDK v2 offers `Resolve(fn)`: a tool parameter filled by our function, left out of the tool's input schema so the model can neither see nor set it.
- **Options considered:** A. `Resolve(fn)` from the validated token (ADR-050) - built in, visible in the signature, testable, never in the model schema; tied to SDK v2. B. Keep the manual helper - works, easy to forget, identity not visible. C. Middleware + context variable - framework-neutral, hidden.
- **Decision:** A. One resolver turns the validated token claims into `Customer(id=sub, scopes=...)`; scope rules declared per tool, e.g. `Resolve(customer_with("orders:write"))` for place/cancel. Not logged in or missing scope -> tool error with a short sentence ("Please log in to see your orders"); the agent turns it into a login prompt. A unit test lists every orders tool and fails if one lacks a resolved customer parameter.
- **Consequences:** `_customer(ctx)` and the `X-Customer-Id` header go away in MCP. Tools become easy to test with a fake resolver. Depends on ADR-050 (validated token in the request context).

## ADR-052 - Confirmation through MCP elicitation (M3)
- **Context:** Quote-then-yes lives in the agent today: the agent swaps `place_order` for a quote and places the order in code when the customer types "yes". MCP itself does not enforce it (any MCP client can call `place_order`), "yes" is parsed from free text, and placing is not idempotent (to-do gap). Spec 2026-07-28 removes server-to-client requests and adds multi round-trip requests: a tool answers `input_required`, the client asks the user and resends the request with the answers.
- **Options considered:** A. `Elicit` inside the MCP tool - server-enforced, real buttons, standard MCP, quote id doubles as idempotency key; needs pause/resume in the agent, new contract events, a button endpoint. B. Keep agent-side quote-then-yes - works, enforced only by our agent, free-text yes. C. Two-step API with a signed `quoteId` - server-enforced and simple, but no elicitation and still free-text yes.
- **Decision:** A. `place_order` and `cancel_order` always return `input_required` with a confirm form (quote summary or order summary, `confirm: boolean`) and a `quoteId` on the first call; they complete only when resent with `confirm: true`. Agent: LangGraph interrupt with a persisted checkpoint; publishes `confirmation.requested` to the conversation stream; resumes when the Node server receives `confirmation.answered` from the browser's buttons. On resume MCP re-quotes and rejects if price or stock changed (returns the new quote). Unanswered confirmations expire after 15 minutes. Services stores `quoteId` with a unique constraint so a repeated place returns the first order.
- **Consequences:** Chat contract gains `confirmation.requested` (event) and `confirmation.answered` (request) with examples and tests (ADR-024, ADR-044). Agent needs a checkpointer (Redis or Postgres - decide at build) and the current quote-then-yes code is removed. Node server gets a confirmation endpoint; Angular shows a confirmation card. Closes the place-order idempotency to-do. Replaces the "Order confirmation" row in buywise-docs/09 section 4 when built.

## ADR-053 - MCP tool annotations (M4)
- **Context:** MCP tools can declare `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`. They are hints (trust them only from trusted servers); all our servers are first-party. Today the agent's safety rules are hard-coded by tool name.
- **Options considered:** A. Annotate every tool and drive agent policy from them. B. Annotate as information only. C. No annotations.
- **Decision:** A. Read-only + idempotent: search_products, get_product, list_stores, check_stock, list_my_orders, get_order, quote_order. place_order: not read-only, not destructive, idempotent (by `quoteId`, ADR-052). cancel_order: not read-only, destructive, idempotent (second cancel returns the same result). All `openWorldHint: false`. Agent policy: a tool that is not read-only must go through confirmation (ADR-052); read-only or idempotent tools may be retried once on timeout; read-only results may be cached within one turn. A test fails if a non-read-only tool does not elicit confirmation or annotations disagree with behaviour.
- **Consequences:** New tools get safe behaviour by declaring hints, not by editing the agent. cancel_order must change from 409 on a repeat to returning the already-cancelled order (idempotent).
- **Details decided at build (2026-11-22, architect):** annotations describe today's behaviour, so `place_order` is `idempotentHint: false` until step 5 adds `quoteId` (ADR-052). Cancel idempotency and the cancel race are fixed in services (one `UPDATE ... WHERE status IN (...) RETURNING`; stock released only when the row changed; a repeat returns the cancelled order). Until step 5 the agent confirms every non-read-only tool itself (place shows a quote, cancel shows the order, both wait for "yes"). Retry: once, after 0.5 s, only on `retryable` errors of read-only or idempotent tools; an open circuit is not retryable. The agent discovers tools from MCP (`list_tools`, cached for the server's `ttlMs`, ADR-057) and no longer keeps its own copies of names, descriptions or schemas; a tool without annotations is treated as a non-idempotent destructive write.

## ADR-054 - MCP structured output (M5)
- **Context:** Tools return plain dicts that reach the model as text; nothing checks their shape. The spec lets a tool declare an `outputSchema` and return matching `structuredContent` plus a text version; SDK v2 generates the schema from a Pydantic return type.
- **Options considered:** A. Pydantic model for every tool result. B. Keep plain dicts.
- **Decision:** A. One Pydantic model per result (e.g. `ProductSummary`, `StockReport`, `OrderSummary`, `Quote`); the SDK validates results against the generated schema; a short text summary is kept for the model; the agent builds `block.product_card` and the confirmation card from `structuredContent`, not by parsing text. Output (and input) schemas are snapshot-tested (M15).
- **Consequences:** Same "strict write" rule as the chat contract (ADR-044) inside MCP. Renaming a result field becomes a visible, tested change. Some duplication between MCP models and services JSON (acceptable; MCP shapes data for the model).
- **Details decided at build (2026-11-22, architect):** snake_case for every argument and result field (MCP maps from services camelCase; the agent maps to the camelCase chat contract); money is `Decimal` inside MCP and a JSON number with 2 decimals for the model (`Money` type, schema `number`), totals carry `currency: "USD"`; every result is an object (no bare lists), results are strict (`extra="forbid"`) and immutable; delivery addresses reduced to city and state (ADR-036). Version 1 keeps the 9 tools; new tools come with their features.

## ADR-055 - MCP errors (M6)
- **Context:** MCP passes the service's error text through as a tool error; AI-facing hints ("Call get_product to find the exact sku") live in the Java services; timeouts and 5xx are not distinguished from business errors.
- **Options considered:** A. Typed error scheme. B. Keep passing text through.
- **Decision:** A. Tool errors (`isError: true`) carry structured content `{code, message, retryable, hint?}`; codes `not_found`, `conflict`, `invalid_input`, `not_logged_in`, `forbidden`, `unavailable`. MCP maps services HTTP status to a code (404, 409, 400, 401, 403, 5xx/timeout -> `unavailable`, retryable). Model-facing hints are written in MCP; services return plain business messages. Circuit breaker per service base URL (open after repeated failures, short cool-down). Protocol (JSON-RPC) errors only for unknown tool / invalid arguments. No stack traces, SQL or internal URLs in any error.
- **Consequences:** Services error messages are cleaned of AI hints (services gap list). The agent can decide retry vs tell the customer from `retryable`. Error codes are part of the tool output schema (ADR-054) and tested.
- **Details decided at build (2026-11-22, architect):** own small circuit breaker in `core/services.py` (opens after 5 consecutive 5xx/429/timeouts, 10 s open, then one half-open trial; business 4xx never open it); MCP never retries (a retried write could place an order twice) - the agent decides from `retryable`; 5xx detail is never passed on. Bad arguments are rejected by the SDK before the tool runs (plain-text validation error). Resolvers (`Resolve`) cannot raise typed errors through the SDK, so they return `Unresolved(code, message)` and `@typed_errors` answers with the typed error without running the tool.

## ADR-056 - MCP per-tool control without an internal gateway (M7)
- **Context:** Spec 2026-07-28 puts the method and tool name in `Mcp-Method` / `Mcp-Name` headers so gateways can route and authorize per tool. Our design has Envoy only at the edge ("no internal gateway"); agent -> MCP is internal.
- **Options considered:** A. Keep no internal gateway; MCP middleware uses the headers. B. Add an internal Envoy between agent and MCP (reverses the earlier decision).
- **Decision:** A. A Starlette middleware in buywise-mcp reads the headers before the tool runs: per-tool and per-customer rate limits with Redis counters (ADR-032), per-tool metrics and structured logs, and a per-tool kill switch (config/Redis flag). A service mesh can take over header-based policy in production later without code changes.
- **Consequences:** "No internal gateway" stays. Rate-limit rejections return a typed `unavailable`/retryable error (ADR-055). Redis gains rate-limit keys (part of the Redis design walkthrough).

## ADR-057 - MCP caching (M8)
- **Context:** The agent lists tools on every turn. Spec 2026-07-28 makes list results cacheable with `ttlMs` and `cacheScope`.
- **Options considered:** A. Cache tool lists and read-only results. B. No caching.
- **Decision:** A. Each MCP server marks its tool list cacheable for 10 minutes with shared scope (same tools for every user); the agent caches per server and refreshes early when the server version changes (deploy). Read-only tool results (ADR-053) are cached within one turn only.
- **Consequences:** Fewer round trips per turn. Tool description changes reach the agent within 10 minutes or on deploy. No cross-turn result caching, so prices and stock stay fresh.

## ADR-058 - MCP resources (M9)
- **Context:** Only MCP tools are used. Resources are read-only data at a URI, loaded by the application for context (tools are chosen by the model to act). The agent fetches the store list with special code (`stores_line()`), and RAG citations point to nothing a customer can open.
- **Options considered:** A. Expose stores, categories and policy documents as resources. B. Tools only.
- **Decision:** A. Inventory server: `buywise://stores`, `buywise://stores/{id}` (resource template). Catalog server: `buywise://catalog/categories`. New `knowledge` MCP server (`/mcp/knowledge`): `buywise://policies/{doc}` serving the published source documents (ADR-033/039 document store), never the agent's database (ADR-010 ownership). The agent loads the store list as a resource instead of `stores_line()`; RAG citations carry the resource URI so the UI and staff can open the exact text. RAG search itself stays in the agent.
- **Consequences:** ADR-031 server list grows (catalog, inventory, orders, knowledge, helpdesk). Resource lists are cacheable like tool lists (ADR-057). Chat contract citation shape gains a `uri` field (ADR-024 change, with examples and tests).

## ADR-059 - MCP prompts (M10)
- **Context:** All prompt text lives in the agent. MCP servers can offer prompt templates; customers type free chat and would not pick prompts themselves.
- **Options considered:** A. Domain prompts on the MCP servers. B. All prompts in the agent.
- **Decision:** A. Each domain server offers its task prompts (catalog: `compare_products`; orders: `order_help`; helpdesk: `handoff_summary`; more as needed), versioned and tested with its tools. The intent router (ADR-030) loads the matching prompt for a routed intent; the staff console shows prompts as quick actions (phase 5). The agent keeps only its core system prompt (trust rules, tone).
- **Consequences:** Domain instructions change with the domain's tools in one place. Prompt lists are cacheable (ADR-057). Prompt changes are covered by tool-description evals (M15).

## ADR-060 - MCP Tasks for staff handoff (M11)
- **Context:** "Talk to a person" creates a ticket and then waits minutes for staff. The Tasks extension (`io.modelcontextprotocol/tasks`, spec 2026-07-28) lets a tool call return a task whose status the client follows and whose result arrives later.
- **Options considered:** A. Tasks on a new helpdesk server. B. Plain tool + events outside MCP.
- **Decision:** A. New `/mcp/helpdesk` server; `request_staff_handoff` returns a Task: `queued` -> `accepted` (staff name) -> `ended` (or `expired`). The agent maps status changes to the existing chat events `handoff.requested`, `handoff.accepted`, `handoff.ended`. Ticket and conversation ownership stay in services helpdesk (ADR-037). Built with the staff console (phase 5).
- **Consequences:** ADR-031 gains the helpdesk server. Agent needs task tracking across turns (with the ADR-052 checkpointer). Confirms that the helpdesk module in services is needed in phase 5.

## ADR-061 - MCP Apps, hybrid (M12)
- **Context:** MCP Apps (extension in spec 2026-07-28): a tool declares an HTML UI template that the host renders in a sandboxed iframe; UI actions flow back as tool calls. Our product and confirmation cards are rendered natively by Angular from typed chat events (ADR-024), accessible (ADR-025) and on brand.
- **Options considered:** A. Hybrid: native cards stay, one MCP App widget. B. MCP Apps for all cards. C. No MCP Apps.
- **Decision:** A. `block.product_card` and the confirmation card (ADR-052) stay native. The catalog server offers one MCP App: a product comparison table with a variant picker (`compare_products` tool + UI resource). The chat contract gains `block.app` (resource URI, title, size hints); Angular renders it in a sandboxed iframe (no same-origin, strict CSP, postMessage bridge that only forwards declared tool calls through the agent).
- **Consequences:** New contract event with examples and tests. Widget accessibility must be checked separately (axe in the iframe). Clicks in the widget go through the agent and the same auth/confirmation rules as any tool call.

## ADR-062 - MCP progress, cancellation, paging, logging (M13)
- **Context:** Core MCP utilities unused: progress updates, cancellation, cursor pagination, logging.
- **Options considered:** A. Use all four. B. Paging only.
- **Decision:** A. Slow tools (e.g. stock at all stores, comparison) report progress; the agent turns it into `status.updated` ("Checking 12 stores..."). When the customer stops a reply or the SSE connection closes for good, the agent cancels in-flight tool calls. `list_my_orders` and `search_products` page with an opaque cursor. Server logs are structured JSON to the observability stack (ADR-063); MCP log messages to the client are not used (no internal detail to the model).
- **Consequences:** Agent needs a cancel path from the Node server ("stop" in the chat contract). Paging changes the tool output schemas (ADR-054).

## ADR-063 - MCP observability with OpenTelemetry (M14)
- **Context:** SDK v2 emits OpenTelemetry tool spans by default; nothing collects them. Full observability stack is phase 7 (parked).
- **Options considered:** A. Build tracing with the MCP phase. B. Wait for phase 7.
- **Decision:** A. W3C `traceparent` propagated agent -> MCP -> services; spans per tool call with tool name, result/error code, duration, retry count; customer ids hashed, no personal data (ADR-036). Export via OTLP to a local OpenTelemetry Collector and a trace viewer container in compose. Metrics from the M7 middleware (calls, errors, latency per tool). Phase 7 reuses this and adds the rest (Grafana stack, Langfuse).
- **Consequences:** Small, explicit exception to "production setup parked": tracing comes forward because the architect wants MCP built production-grade. Two new local containers.

## ADR-064 - MCP tool versioning and testing (M15)
- **Context:** Tool names, descriptions, schemas and annotations are the contract with the model; changing a description changes AI behaviour. Only a smoke script exists.
- **Options considered:** A. Full set. B. Snapshot tests only.
- **Decision:** A. Snapshot file per server (names, descriptions, input/output schemas, annotations, prompts, resources) in git; CI fails on an unreviewed change. Breaking change (removed/renamed argument or result field) = new tool name or server major version, never silent. Integration tests use the SDK `Client` against real MCP + services (Testcontainers). MCP Inspector for manual exploration. Tool-choice evals: a question set checks the model picks the right tool and arguments; run on every description/prompt change (joins the router eval set, ADR-030).
- **Consequences:** Description edits become reviewed, measured changes. Eval runs need the local LLM (slow; run on demand and in nightly CI).

