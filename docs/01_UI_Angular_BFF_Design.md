# UI + BFF - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Purpose and responsibilities
- **Angular web app:** customer chat widget, product cards, cart summary, order status view; staff console (ticket queue, take over chat).
- **NestJS BFF:** login/session, token exchange, WebSocket streaming of agent replies, screen aggregation. No business logic.

## 2. Technology and versions
| Part | Choice | Why |
|---|---|---|
| Web | Angular 22 (signals, Signal Forms, zoneless, Vitest), TypeScript 6 | Stable signal-first APIs, long support window |
| BFF | Node.js 24 LTS, NestJS 11 + Fastify adapter | Structure (modules, DI, guards), WebSocket gateways, fast HTTP engine |
| Component library | TBD | Open decision |

## 3. Module structure
```
ui/
├── web/   # Angular 22
└── bff/   # NestJS 11
```

## 4. Interfaces
- Web <-> BFF: REST (screens) + WebSocket (chat stream).
- BFF -> Agent API: chat requests, streamed responses.
- BFF -> internal gateway: order history, staff console data.

## 5. Key flows
- TBD (chat streaming, login, staff takeover).

## 6. Non-functional
- TBD (session handling, reconnect, accessibility, browser support).

## 7. Testing
- Vitest (web), Jest (BFF), Playwright end-to-end - TBD.

## 8. Open decisions
1. Component library.
2. Session model: BFF cookie session vs token in browser.
