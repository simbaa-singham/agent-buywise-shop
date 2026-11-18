# buywise-web

Customer web app and staff console (Angular 22) plus the Node server (NestJS 12 on Fastify), shipped as one deployable. Owns the chat message contract shared with the agent.

**Open in:** WebStorm -> open the `buywise-web/` folder. Three npm projects: the workspace root (`package.json`, holds the chat contract package), `web/` (Angular) and `server/` (Node server), each with its own `npm install` (`make install` does all). Git is detected from the repo root automatically.

## Contents
| Path | Purpose |
|---|---|
| `package.json` | npm workspaces root (run `npm install` here) |
| `web/` | Angular workspace: customer-web (built), staff-console (designed), shared |
| `web/projects/shared/contracts/` | Chat contract: JSON Schema, examples, generated TypeScript (ADR-024) |
| `server/` | Node server (NestJS 12 + Fastify): login, session, chat API, SSE; serves the Angular build (npm package `buywise-server`) |
| `Makefile` | install, build, run, contracts, contracts-check |
| `../buywise-docs/01-buywise-web/` | 01-design.md, 02-learning.md (docs live in buywise-docs, ADR-048) |

## Run
`make contracts` (regenerate TypeScript + Python contract types), `make contracts-check` (CI drift check).

## Documents
- [buywise-docs/01-buywise-web/01-design.md](../buywise-docs/01-buywise-web/01-design.md) - detailed design
- [buywise-docs/01-buywise-web/02-learning.md](../buywise-docs/01-buywise-web/02-learning.md) - learning notes per phase
- System overview: [buywise-docs/00-architecture-overview.md](../buywise-docs/00-architecture-overview.md); roadmap: [buywise-docs/09-implementation-roadmap.md](../buywise-docs/09-implementation-roadmap.md)

## Decisions that apply (central log: buywise-docs/10-adr/01-adr-log.md)
| ADR | Decision |
|---|---|
| [ADR-003](../buywise-docs/10-adr/01-adr-log.md) | Angular 22 for the web UI (chosen over 21: stable signal APIs, longer support) |
| [ADR-004](../buywise-docs/10-adr/01-adr-log.md) | NestJS 11 + Fastify Node server on Node.js 24 LTS; serves the Angular build (one deployable) |
| [ADR-018](../buywise-docs/10-adr/01-adr-log.md) | UI app structure: one Angular workspace with two apps (customer-web, staff-console) + shared library; one deployable |
| [ADR-019](../buywise-docs/10-adr/01-adr-log.md) | Angular Material (Material 3) + CDK with custom theme; SCSS + design tokens, no Tailwind; custom chat UI on CDK |
| [ADR-020](../buywise-docs/10-adr/01-adr-log.md) | Browser real-time channel: SSE (server -> browser) + HTTP POST (browser -> server); Redis pub/sub across pods (amended by ADR-029: Redis Streams), ... |
| [ADR-021](../buywise-docs/10-adr/01-adr-log.md) | Session pattern: Node server session (token handler), tokens in Redis, opaque `__Host-` cookie; guest sessions; separate staff session with MFA |
| [ADR-022](../buywise-docs/10-adr/01-adr-log.md) | UI state: NgRx SignalStore for shared/live state, plain signals for local state, `httpResource` for read-only server data |
| [ADR-023](../buywise-docs/10-adr/01-adr-log.md) | UI rendering: hybrid per route - prerender product/category pages, client rendering elsewhere; no per-request SSR |
| [ADR-024](../buywise-docs/10-adr/01-adr-log.md) | Chat message contract: own versioned JSON Schema envelope, AG-UI-shaped reply events, structured blocks, Redis Stream replay (amended by ADR-029: S... |
| [ADR-025](../buywise-docs/10-adr/01-adr-log.md) | Accessibility: WCAG 2.2 AA enforced by angular-eslint + axe-core in CI plus a manual per-release checklist; chat-specific rules |
| [ADR-027](../buywise-docs/10-adr/01-adr-log.md) | LLM observability in the UI: Grafana for trends/alerts + staff-console AI Operations (ops-admin) + customer-web dev overlay; `status.updated` and `... |
| [ADR-029](../buywise-docs/10-adr/01-adr-log.md) | Agent output path: background turns (`POST /turns` 202); agent appends ADR-024 events to per-conversation Redis Stream; Node server pods read and forward; ... |
| [ADR-036](../buywise-docs/10-adr/01-adr-log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-037](../buywise-docs/10-adr/01-adr-log.md) | Conversation ownership owned by the helpdesk module in `buywise-services`; Node server caches in Redis; agent paused/resumed as second check |
| [ADR-038](../buywise-docs/10-adr/01-adr-log.md) | AI Operations charts: Apache ECharts (modular imports) with own thin signal-based wrapper; "view as table" accessibility toggle |
