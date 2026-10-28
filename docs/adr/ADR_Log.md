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
| ADR-010 | PostgreSQL, one database, schema per module | Proposed | 2026-10-28 |
| ADR-011 | Postgres + pgvector + full-text for RAG | Proposed | 2026-10-28 |
| ADR-012 | Project name agent-buywise-shop; electronics shopping assistant, Apple products as sample catalog | Accepted | 2026-10-28 |
| ADR-013 | Local-first, small-scale runtime; production sizing via configuration only | Accepted | 2026-10-28 |
| ADR-014 | One Spring Boot 4.1 modular monolith (Spring Modulith 2.x), controllers per use case | Accepted | 2026-10-28 |
| ADR-015 | `buywise-mcp` as separate deployable, MCP Python SDK v2, spec 2026-07-28, wrapping REST APIs | Accepted | 2026-10-28 |
| ADR-016 | Six deployables: web, services, agent, mcp, event-publisher, event-consumers | Accepted | 2026-10-28 |
| ADR-017 | Envoy Gateway at the edge; no internal gateway; Spring Security in services; service mesh as future option | Accepted | 2026-10-28 |
| ADR-018 | UI app structure: one Angular workspace with two apps (customer-web, staff-console) + shared library; one deployable | Accepted | 2026-10-28 |
| ADR-019 | Angular Material (Material 3) + CDK with custom theme; SCSS + design tokens, no Tailwind; custom chat UI on CDK | Accepted | 2026-10-28 |
| ADR-020 | Browser real-time channel: SSE (server -> browser) + HTTP POST (browser -> server); Redis pub/sub across pods, no sticky sessions; WebSocket as planned upgrade for staff takeover | Accepted | 2026-10-28 |
| ADR-021 | Session pattern: BFF session (token handler), tokens in Redis, opaque `__Host-` cookie; guest sessions; separate staff session with MFA | Accepted | 2026-10-28 |
| ADR-022 | UI state: NgRx SignalStore for shared/live state, plain signals for local state, `httpResource` for read-only server data | Accepted | 2026-10-28 |
| ADR-023 | UI rendering: hybrid per route - prerender product/category pages, client rendering elsewhere; no per-request SSR | Accepted | 2026-10-28 |
| ADR-024 | Chat message contract: own versioned JSON Schema envelope, AG-UI-shaped reply events, structured blocks, Redis Stream replay, idempotent sends | Accepted | 2026-10-28 |
| ADR-025 | Accessibility: WCAG 2.2 AA enforced by angular-eslint + axe-core in CI plus a manual per-release checklist; chat-specific rules | Accepted | 2026-10-28 |

## Deferred decisions
| Topic | Options | Decide at |
|---|---|---|
| Event publishing mechanism | Polling outbox relay vs Debezium CDC | Implementation of events |
| RAG re-indexing location | Agent vs event consumers | Implementation of RAG |

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
