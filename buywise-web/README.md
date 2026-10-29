# buywise-web

Customer web app and staff console (Angular 22) plus the BFF (NestJS 11 on Fastify), shipped as one deployable. Owns the chat message contract shared with the agent.

**Open in:** WebStorm -> open the `buywise-web/` folder (npm workspaces: the contract today; `web` and `bff` join in phase 1). Git is detected from the repo root automatically.

## Contents
| Path | Purpose |
|---|---|
| `package.json` | npm workspaces root (run `npm install` here) |
| `web/` | Angular workspace: customer-web, staff-console, shared (built from phase 1) |
| `web/projects/shared/contracts/` | Chat contract: JSON Schema, examples, generated TypeScript (ADR-024) |
| `bff/` | NestJS BFF (built from phase 1) |
| `Makefile` | contracts, contracts-check |
| `docs/` | design.md, learning.md |

## Run
`make contracts` (regenerate TypeScript + Python contract types), `make contracts-check` (CI drift check).

## Documents
- [docs/design.md](docs/design.md) - detailed design
- [docs/learning.md](docs/learning.md) - learning notes per phase
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-003](../docs/adr/ADR_Log.md) | Angular 22 for the web UI (chosen over 21: stable signal APIs, longer support) |
| [ADR-004](../docs/adr/ADR_Log.md) | NestJS 11 + Fastify BFF on Node.js 24 LTS; serves the Angular build (one deployable) |
| [ADR-018](../docs/adr/ADR_Log.md) | UI app structure: one Angular workspace with two apps (customer-web, staff-console) + shared library; one deployable |
| [ADR-019](../docs/adr/ADR_Log.md) | Angular Material (Material 3) + CDK with custom theme; SCSS + design tokens, no Tailwind; custom chat UI on CDK |
| [ADR-020](../docs/adr/ADR_Log.md) | Browser real-time channel: SSE (server -> browser) + HTTP POST (browser -> server); Redis pub/sub across pods (amended by ADR-029: Redis Streams), ... |
| [ADR-021](../docs/adr/ADR_Log.md) | Session pattern: BFF session (token handler), tokens in Redis, opaque `__Host-` cookie; guest sessions; separate staff session with MFA |
| [ADR-022](../docs/adr/ADR_Log.md) | UI state: NgRx SignalStore for shared/live state, plain signals for local state, `httpResource` for read-only server data |
| [ADR-023](../docs/adr/ADR_Log.md) | UI rendering: hybrid per route - prerender product/category pages, client rendering elsewhere; no per-request SSR |
| [ADR-024](../docs/adr/ADR_Log.md) | Chat message contract: own versioned JSON Schema envelope, AG-UI-shaped reply events, structured blocks, Redis Stream replay (amended by ADR-029: S... |
| [ADR-025](../docs/adr/ADR_Log.md) | Accessibility: WCAG 2.2 AA enforced by angular-eslint + axe-core in CI plus a manual per-release checklist; chat-specific rules |
| [ADR-027](../docs/adr/ADR_Log.md) | LLM observability in the UI: Grafana for trends/alerts + staff-console AI Operations (ops-admin) + customer-web dev overlay; `status.updated` and `... |
| [ADR-029](../docs/adr/ADR_Log.md) | Agent output path: background turns (`POST /turns` 202); agent appends ADR-024 events to per-conversation Redis Stream; BFF pods read and forward; ... |
| [ADR-036](../docs/adr/ADR_Log.md) | PII policy: 4-tier classification; Presidio placeholders before LLM calls; field-level envelope encryption + blind index for email/phone/address; m... |
| [ADR-037](../docs/adr/ADR_Log.md) | Conversation ownership owned by the helpdesk module in `buywise-services`; BFF caches in Redis; agent paused/resumed as second check |
| [ADR-038](../docs/adr/ADR_Log.md) | AI Operations charts: Apache ECharts (modular imports) with own thin signal-based wrapper; "view as table" accessibility toggle |
